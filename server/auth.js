// auth.js — Registration, Login, Logout, JWT middleware
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const router = express.Router();
const logger = require('./logger');

const {
  db, getUserByEmail, getUserById, safeUser,
  getUniqueCode, getUniqueAccountNumber, getUserByPhone
} = require('./db');

const JWT_SECRET = process.env.JWT_SECRET || 'fundtrace_jwt_secret_change_in_production_2024';
const JWT_EXPIRES = '7d';
const BCRYPT_ROUNDS = 12;

// ─── MIDDLEWARE ──────────────────────────────────────────────────────────────

// Verify JWT from httpOnly cookie
function requireAuth(req, res, next) {
  const token = req.cookies?.ft_token;
  if (!token) return res.status(401).json({ error: 'Not authenticated' });

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    // Check session still valid in DB
    const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
    const session = db.prepare(
      'SELECT * FROM sessions WHERE token_hash = ? AND expires_at > ? AND user_id = ?'
    ).get(tokenHash, Math.floor(Date.now() / 1000), payload.userId);

    if (!session) return res.status(401).json({ error: 'Session expired. Please log in again.' });

    req.userId = payload.userId;
    req.userRole = payload.role;
    next();
  } catch (e) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}

// Officer-only middleware
function requireOfficer(req, res, next) {
  requireAuth(req, res, () => {
    if (req.userRole !== 'officer') {
      return res.status(403).json({ error: 'Officer access required' });
    }
    next();
  });
}

// ─── HELPERS ─────────────────────────────────────────────────────────────────

function issueToken(res, user) {
  const token = jwt.sign(
    { userId: user.id, role: user.role },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES }
  );

  const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
  const expiresAt = Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60; // 7 days

  // Store session in DB
  db.prepare(
    'INSERT INTO sessions (user_id, token_hash, expires_at) VALUES (?, ?, ?)'
  ).run(user.id, tokenHash, expiresAt);

  // httpOnly cookie — JS cannot read this (XSS protection)
  res.cookie('ft_token', token, {
    httpOnly: true,
    secure: false,        // set true in production with HTTPS
    sameSite: 'strict',
    maxAge: 7 * 24 * 60 * 60 * 1000
  });

  return token;
}

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePassword(password) {
  // Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
  const errors = [];
  if (password.length < 8) errors.push('At least 8 characters');
  if (!/[A-Z]/.test(password)) errors.push('At least one uppercase letter');
  if (!/[a-z]/.test(password)) errors.push('At least one lowercase letter');
  if (!/[0-9]/.test(password)) errors.push('At least one number');
  if (!/[^A-Za-z0-9]/.test(password)) errors.push('At least one special character (!@#$%^&*)');
  return errors;
}

function normalizePhone(raw) {
  if (!raw) return '';
  const s = String(raw).trim();
  // Remove spaces, dashes, parentheses; keep leading + if present
  const cleaned = s.replace(/[\s()-]/g, '');
  // Standardize by removing leading +
  return cleaned.startsWith('+') ? cleaned.slice(1) : cleaned;
}

// Check brute force — max 10 failed attempts per email in 15 min
function checkBruteForce(email, ip) {
  // const windowStart = Math.floor(Date.now() / 1000) - 15 * 60;
  // TEMP: 5-second brute-force window for testing
  const windowStart = Math.floor(Date.now() / 1000) - 5;
  const attempts = db.prepare(
    'SELECT COUNT(*) as cnt FROM login_attempts WHERE email = ? AND success = 0 AND created_at > ?'
  ).get(email.toLowerCase(), windowStart);
  return attempts.cnt >= 10;
}

// ─── ROUTES ──────────────────────────────────────────────────────────────────

// POST /api/auth/register
router.post('/register', async (req, res) => {
  try {
    const { full_name, email, phone, password, branch, account_type } = req.body;

    // Validate inputs
    if (!full_name || !email || !phone || !password) {
      return res.status(400).json({ error: 'Name, email, phone and password are required' });
    }
    if (!validateEmail(email)) {
      return res.status(400).json({ error: 'Invalid email address' });
    }
    const phoneNorm = normalizePhone(phone || '');
    if (!/^[0-9]{8,15}$/.test(phoneNorm)) {
      return res.status(400).json({ error: 'Invalid phone number' });
    }
    const pwErrors = validatePassword(password);
    if (pwErrors.length > 0) {
      return res.status(400).json({ error: 'Password requirements not met', details: pwErrors });
    }
    if (full_name.trim().length < 2) {
      return res.status(400).json({ error: 'Full name must be at least 2 characters' });
    }

    // Check duplicate email
    const existing = getUserByEmail(email);
    if (existing) {
      return res.status(409).json({ error: 'An account with this email already exists' });
    }
    // Check duplicate phone
    const existingPhone = getUserByPhone(phoneNorm);
    if (existingPhone) {
      return res.status(409).json({ error: 'An account with this phone number already exists' });
    }

    // Hash password with bcrypt (12 rounds — slow enough to resist brute force)
    const password_hash = await bcrypt.hash(password, BCRYPT_ROUNDS);

    const unique_code = getUniqueCode();
    const account_number = getUniqueAccountNumber();

    const result = db.prepare(`
      INSERT INTO users (unique_code, full_name, email, phone, password_hash, role, balance, account_number, branch, account_type, last_active)
      VALUES (?, ?, ?, ?, ?, 'client', 10000.00, ?, ?, ?, ?)
    `).run(
      unique_code,
      full_name.trim(),
      email.toLowerCase().trim(),
      phoneNorm,
      password_hash,
      account_number,
      branch || 'Mumbai-Main',
      account_type || 'Savings',
      Math.floor(Date.now() / 1000)
    );

    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(result.lastInsertRowid);

    // Welcome notification
    db.prepare(`
      INSERT INTO notifications (user_id, type, title, body, data)
      VALUES (?, 'system', ?, ?, ?)
    `).run(
      user.id,
      'Welcome to FundTrace Bank!',
      `Your account has been created. Your unique ID is ${unique_code}. You have been credited ₹10,000 as a welcome bonus.`,
      JSON.stringify({ unique_code, account_number, bonus: 10000 })
    );

    issueToken(res, user);
    try {
      logger.register({ user_code: user.unique_code, account_number: user.account_number, branch: user.branch, account_type: user.account_type });
    } catch (e) {}

    return res.status(201).json({
      success: true,
      message: 'Account created successfully',
      user: safeUser(user)
    });

  } catch (err) {
    console.error('Register error:', err);
    return res.status(500).json({ error: 'Server error during registration' });
  }
});

// POST /api/auth/login (email or phone + password)
router.post('/login', async (req, res) => {
  try {
    const { identifier, email, phone, password } = req.body;
    const principalRaw = (identifier || email || phone || '').trim();
    const principalPhoneNorm = normalizePhone(principalRaw);
    const ip = req.ip || req.connection.remoteAddress;

    if (!principalRaw || !password) {
      return res.status(400).json({ error: 'Email/phone and password are required' });
    }

    // Brute force check
    const bruteKey = validateEmail(principalRaw) ? principalRaw : principalPhoneNorm;
    if (checkBruteForce(bruteKey, ip)) {
      return res.status(429).json({
        error: 'Too many failed attempts. Please wait 15 minutes before trying again.'
      });
    }

    let user = null;
    if (validateEmail(principalRaw)) {
      user = getUserByEmail(principalRaw);
    } else {
      // Try exact, then normalized variant
      user = getUserByPhone(principalRaw) || getUserByPhone(principalPhoneNorm);
    }

    // Log attempt
    const logAttempt = db.prepare(
      'INSERT INTO login_attempts (email, ip_address, success) VALUES (?, ?, ?)'
    );

    if (!user) {
      logAttempt.run(bruteKey.toLowerCase(), ip, 0);
      // Generic message — don't reveal whether email exists
      try { logger.login({ user_code: null, user_name: null, status: 'failed', ip }); } catch (e) {}
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    const passwordMatch = await bcrypt.compare(password, user.password_hash);
    if (!passwordMatch) {
      logAttempt.run(bruteKey.toLowerCase(), ip, 0);
      try { logger.login({ user_code: user.unique_code, user_name: user.full_name, status: 'failed', ip }); } catch (e) {}
      return res.status(401).json({ error: 'Invalid email or password' });
    }

    if (user.status === 'frozen') {
      logAttempt.run(bruteKey.toLowerCase(), ip, 0);
      try { logger.login({ user_code: user.unique_code, user_name: user.full_name, status: 'frozen', ip }); } catch (e) {}
      return res.status(403).json({ error: 'This account has been frozen. Contact support.' });
    }

    // Success
    logAttempt.run(bruteKey.toLowerCase(), ip, 1);

    // Update last_active
    db.prepare('UPDATE users SET last_active = ? WHERE id = ?')
      .run(Math.floor(Date.now() / 1000), user.id);

    issueToken(res, user);
    try { logger.login({ user_code: user.unique_code, user_name: user.full_name, status: 'success', ip }); } catch (e) {}

    return res.json({
      success: true,
      user: safeUser(user)
    });

  } catch (err) {
    console.error('Login error:', err);
    return res.status(500).json({ error: 'Server error during login' });
  }
});

// POST /api/auth/logout
router.post('/logout', requireAuth, (req, res) => {
  try {
    const token = req.cookies?.ft_token;
    if (token) {
      const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
      db.prepare('DELETE FROM sessions WHERE token_hash = ?').run(tokenHash);
    }
    res.clearCookie('ft_token');
    return res.json({ success: true });
  } catch (err) {
    return res.status(500).json({ error: 'Logout error' });
  }
});

// GET /api/auth/me — get current user from cookie
router.get('/me', requireAuth, (req, res) => {
  const user = getUserById(req.userId);
  if (!user) return res.status(404).json({ error: 'User not found' });
  return res.json({ user: safeUser(user) });
});

// GET /api/auth/check — quick auth check, returns 200 or 401
router.get('/check', requireAuth, (req, res) => {
  return res.json({ authenticated: true, role: req.userRole });
});

// PATCH /api/auth/profile — update name/phone/password
router.patch('/profile', requireAuth, async (req, res) => {
  try {
    const { full_name, phone, password_old, password_new } = req.body;
    const user = getUserById(req.userId);
    if (!user) return res.status(404).json({ error: 'User not found' });
    const updates = [];
    const params = [];
    if (full_name && full_name.trim().length >= 2) {
      updates.push('full_name = ?'); params.push(full_name.trim());
    }
    if (phone) {
      const phoneNorm = phone.trim();
      if (!/^\+?[0-9]{8,15}$/.test(phoneNorm)) {
        return res.status(400).json({ error: 'Invalid phone number' });
      }
      const dup = db.prepare('SELECT id FROM users WHERE phone = ? AND id != ?').get(phoneNorm, user.id);
      if (dup) return res.status(409).json({ error: 'Phone number already in use' });
      updates.push('phone = ?'); params.push(phoneNorm);
    }
    if (password_new) {
      if (!password_old) return res.status(400).json({ error: 'Current password required' });
      const ok = await bcrypt.compare(password_old, user.password_hash);
      if (!ok) return res.status(401).json({ error: 'Current password incorrect' });
      const pwErrors = validatePassword(password_new);
      if (pwErrors.length > 0) {
        return res.status(400).json({ error: 'Password requirements not met', details: pwErrors });
      }
      const newHash = await bcrypt.hash(password_new, BCRYPT_ROUNDS);
      updates.push('password_hash = ?'); params.push(newHash);
    }
    if (!updates.length) return res.status(400).json({ error: 'No changes provided' });
    params.push(user.id);
    db.prepare(`UPDATE users SET ${updates.join(', ')} WHERE id = ?`).run(...params);
    const updated = getUserById(user.id);
    return res.json({ success: true, user: safeUser(updated) });
  } catch (e) {
    console.error('Profile update error:', e);
    return res.status(500).json({ error: 'Server error during profile update' });
  }
});

module.exports = { router, requireAuth, requireOfficer };
