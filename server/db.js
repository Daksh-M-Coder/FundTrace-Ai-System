// db.js — SQLite database setup, schema, and helpers
const Database = require('better-sqlite3');
const path = require('path');

const DB_PATH = path.join(__dirname, 'fundtrace.db');
const db = new Database(DB_PATH);

// Enable WAL mode for better concurrent read performance
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

// ─── SCHEMA ─────────────────────────────────────────────────────────────────

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_code TEXT    NOT NULL UNIQUE,
    full_name   TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    phone       TEXT,
    password_hash TEXT  NOT NULL,
    role        TEXT    NOT NULL DEFAULT 'client',  -- 'client' | 'officer'
    balance     REAL    NOT NULL DEFAULT 50000.00,
    account_number TEXT NOT NULL UNIQUE,
    branch      TEXT    NOT NULL DEFAULT 'Mumbai-Main',
    account_type TEXT   NOT NULL DEFAULT 'Savings',
    status      TEXT    NOT NULL DEFAULT 'active',  -- 'active' | 'frozen' | 'dormant'
    last_active INTEGER,
    created_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
  );

  CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT    NOT NULL UNIQUE,
    expires_at  INTEGER NOT NULL,
    ip_address  TEXT,
    created_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
  );

  CREATE TABLE IF NOT EXISTS friends (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    receiver_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status        TEXT    NOT NULL DEFAULT 'pending',  -- 'pending' | 'accepted' | 'rejected'
    created_at    INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    updated_at    INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    UNIQUE(requester_id, receiver_id)
  );

  CREATE TABLE IF NOT EXISTS transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    txn_id          TEXT    NOT NULL UNIQUE,
    from_user_id    INTEGER REFERENCES users(id),
    to_user_id      INTEGER REFERENCES users(id),
    from_account    TEXT    NOT NULL,
    to_account      TEXT    NOT NULL,
    amount          REAL    NOT NULL,
    channel         TEXT    NOT NULL DEFAULT 'IMPS',  -- IMPS | NEFT | RTGS | UPI
    note            TEXT,
    status          TEXT    NOT NULL DEFAULT 'completed', -- completed | failed | pending
    flagged         INTEGER NOT NULL DEFAULT 0,
    fraud_score     REAL    NOT NULL DEFAULT 0,
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
  );

  CREATE TABLE IF NOT EXISTS fraud_alerts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id        TEXT    NOT NULL UNIQUE,
    transaction_id  INTEGER REFERENCES transactions(id),
    user_id         INTEGER REFERENCES users(id),
    pattern_type    TEXT    NOT NULL,  -- circular | layering | structuring | dormant | profile_mismatch
    risk_score      REAL    NOT NULL,
    description     TEXT,
    status          TEXT    NOT NULL DEFAULT 'open',  -- open | reviewing | closed | filed
    assigned_to     INTEGER REFERENCES users(id),
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
  );

  CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type        TEXT    NOT NULL,  -- txn_received | txn_sent | friend_request | friend_accepted | fraud_alert
    title       TEXT    NOT NULL,
    body        TEXT    NOT NULL,
    data        TEXT,              -- JSON blob
    read        INTEGER NOT NULL DEFAULT 0,
    created_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
  );

  CREATE TABLE IF NOT EXISTS login_attempts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT    NOT NULL,
    ip_address  TEXT,
    success     INTEGER NOT NULL DEFAULT 0,
    created_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
  );

  CREATE TABLE IF NOT EXISTS coupons (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    code         TEXT    NOT NULL UNIQUE,
    name         TEXT    NOT NULL,
    description  TEXT,
    amount       REAL    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'new',  -- new | redeemed | expired
    created_by   INTEGER REFERENCES users(id),
    redeemed_by  INTEGER REFERENCES users(id),
    redeemed_at  INTEGER,
    created_at   INTEGER NOT NULL DEFAULT (strftime('%s','now'))
  );

  CREATE INDEX IF NOT EXISTS idx_transactions_from   ON transactions(from_user_id);
  CREATE INDEX IF NOT EXISTS idx_transactions_to     ON transactions(to_user_id);
  CREATE INDEX IF NOT EXISTS idx_transactions_time   ON transactions(created_at);
  CREATE INDEX IF NOT EXISTS idx_fraud_alerts_user   ON fraud_alerts(user_id);
  CREATE INDEX IF NOT EXISTS idx_notifications_user  ON notifications(user_id, read);
  CREATE INDEX IF NOT EXISTS idx_coupons_status      ON coupons(status);
  CREATE INDEX IF NOT EXISTS idx_coupons_redeemed_by ON coupons(redeemed_by);
  CREATE UNIQUE INDEX IF NOT EXISTS idx_users_phone_unique ON users(phone) WHERE phone IS NOT NULL;
`);

// Migrations for existing databases
try {
  const cols = db.prepare("PRAGMA table_info(coupons)").all();
  if (!cols.find(c => c.name === 'description')) {
    db.exec("ALTER TABLE coupons ADD COLUMN description TEXT;");
  }
} catch (e) {}

// ─── HELPERS ─────────────────────────────────────────────────────────────────

// Generate a unique FundTrace client code like FT-X7K2P9
function generateUniqueCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = 'FT-';
  for (let i = 0; i < 6; i++) code += chars[Math.floor(Math.random() * chars.length)];
  return code;
}

// Generate account number like ACC-2024-XXXXXX
function generateAccountNumber() {
  const year = new Date().getFullYear();
  const suffix = Math.floor(100000 + Math.random() * 900000);
  return `ACC-${year}-${suffix}`;
}

// Generate transaction ID like TXN-88201
function generateTxnId() {
  return 'TXN-' + Math.floor(10000 + Math.random() * 90000);
}

// Generate alert ID like ALT-0012
function generateAlertId() {
  const num = Math.floor(1000 + Math.random() * 9000);
  return `ALT-${num}`;
}

// Generate coupon code like CP-XXXXXX
function generateCouponCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = 'CP-';
  for (let i = 0; i < 6; i++) code += chars[Math.floor(Math.random() * chars.length)];
  return code;
}

// Get user by ID
function getUserById(id) {
  return db.prepare('SELECT * FROM users WHERE id = ?').get(id);
}

// Get user by email
function getUserByEmail(email) {
  return db.prepare('SELECT * FROM users WHERE email = ?').get(email.toLowerCase().trim());
}

// Get user by unique code
function getUserByCode(code) {
  return db.prepare('SELECT * FROM users WHERE unique_code = ?').get(code.toUpperCase().trim());
}

// Get user by account number
function getUserByAccount(accountNumber) {
  return db.prepare('SELECT * FROM users WHERE account_number = ?').get(accountNumber);
}

// Get user by phone
function getUserByPhone(phone) {
  return db.prepare('SELECT * FROM users WHERE phone = ?').get(phone);
}

// Safe user object (strip sensitive fields)
function safeUser(user) {
  if (!user) return null;
  const { password_hash, ...safe } = user;
  return safe;
}

// Ensure unique_code is truly unique
function getUniqueCode() {
  let code, exists;
  do {
    code = generateUniqueCode();
    exists = db.prepare('SELECT id FROM users WHERE unique_code = ?').get(code);
  } while (exists);
  return code;
}

function getUniqueAccountNumber() {
  let acc, exists;
  do {
    acc = generateAccountNumber();
    exists = db.prepare('SELECT id FROM users WHERE account_number = ?').get(acc);
  } while (exists);
  return acc;
}

// ─── SEED OFFICER ACCOUNT ────────────────────────────────────────────────────
// Seeds a default bank officer account if none exists
async function seedOfficer() {
  const bcrypt = require('bcrypt');
  const existing = db.prepare("SELECT id FROM users WHERE role = 'officer' LIMIT 1").get();
  if (!existing) {
    const hash = await bcrypt.hash('Officer@123', 12);
    db.prepare(`
      INSERT INTO users (unique_code, full_name, email, password_hash, role, balance, account_number, branch, account_type)
      VALUES (?, ?, ?, ?, 'officer', 0, ?, 'HQ-Mumbai', 'Official')
    `).run('FT-OFFICER', 'Bank Officer', 'officer@fundtrace.bank', hash, 'ACC-OFFICER-001');
    console.log('✅ Officer account seeded: officer@fundtrace.bank / Officer@123');
  }
}

module.exports = {
  db,
  generateUniqueCode,
  generateAccountNumber,
  generateTxnId,
  generateAlertId,
  generateCouponCode,
  getUserById,
  getUserByEmail,
  getUserByCode,
  getUserByAccount,
  getUserByPhone,
  safeUser,
  getUniqueCode,
  getUniqueAccountNumber,
  seedOfficer
};
