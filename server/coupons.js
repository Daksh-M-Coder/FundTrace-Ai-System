const express = require('express');
const router = express.Router();
const { requireAuth, requireOfficer } = require('./auth');
const { db, getUserById, generateCouponCode } = require('./db');
const logger = require('./logger');

// Officer: create coupon
router.post('/create', requireOfficer, (req, res) => {
  const { name, amount, description } = req.body;
  const valid = [10000, 25000, 50000, 100000, 125000, 500000, 1000000];
  const amt = parseFloat(amount);
  if (!name || !amt || !valid.includes(amt)) {
    return res.status(400).json({ error: 'Invalid coupon name or amount' });
  }
  let code, exists;
  do {
    code = generateCouponCode();
    exists = db.prepare('SELECT id FROM coupons WHERE code = ?').get(code);
  } while (exists);
  db.prepare('INSERT INTO coupons (code, name, description, amount, status, created_by) VALUES (?, ?, ?, ?, ?, ?)')
    .run(code, name.trim(), (description || '').trim(), amt, 'new', req.userId);
  return res.status(201).json({ success: true, code });
});

// Officer: list coupons
router.get('/list', requireOfficer, (req, res) => {
  const { status, limit = 100, offset = 0 } = req.query;
  let q = 'SELECT c.*, u.full_name AS created_by_name, r.full_name AS redeemed_by_name FROM coupons c LEFT JOIN users u ON c.created_by = u.id LEFT JOIN users r ON c.redeemed_by = r.id';
  const params = [];
  if (status) { q += ' WHERE c.status = ?'; params.push(status); }
  q += ' ORDER BY c.created_at DESC LIMIT ? OFFSET ?';
  params.push(parseInt(limit), parseInt(offset));
  const rows = db.prepare(q).all(...params);
  const total = db.prepare(`SELECT COUNT(*) as cnt FROM coupons${status ? ' WHERE status = ?' : ''}`).get(...(status ? [status] : []));
  return res.json({ coupons: rows, total: total.cnt });
});

// Client: redeem coupon
router.post('/redeem', requireAuth, (req, res) => {
  const { code } = req.body;
  if (!code) return res.status(400).json({ error: 'Coupon code is required' });
  const coupon = db.prepare('SELECT * FROM coupons WHERE code = ?').get(code.trim().toUpperCase());
  if (!coupon) return res.status(404).json({ error: 'Coupon not found' });
  if (coupon.status !== 'new') return res.status(400).json({ error: 'Coupon already used or expired' });
  const user = getUserById(req.userId);
  if (!user) return res.status(404).json({ error: 'User not found' });

  const redeemTxn = db.transaction(() => {
    db.prepare('UPDATE users SET balance = balance + ? WHERE id = ?').run(coupon.amount, user.id);
    db.prepare('UPDATE coupons SET status = ?, redeemed_by = ?, redeemed_at = ? WHERE id = ?')
      .run('redeemed', user.id, Math.floor(Date.now() / 1000), coupon.id);
    db.prepare(`
      INSERT INTO transactions (txn_id, from_user_id, to_user_id, from_account, to_account, amount, channel, note, status)
      VALUES (?, NULL, ?, ?, ?, ?, 'COUPON', ?, 'completed')
    `).run(
      'TXN-' + Math.floor(10000 + Math.random() * 90000),
      user.id,
      'SYSTEM',
      user.account_number,
      coupon.amount,
      `Redeemed ${coupon.code} (${coupon.name})`
    );
    db.prepare(`INSERT INTO notifications (user_id, type, title, body, data) VALUES (?, 'system', ?, ?, ?)`).run(
      user.id,
      'Coupon redeemed',
      `You redeemed ${coupon.code} for ₹${coupon.amount.toLocaleString('en-IN')}`,
      JSON.stringify({ code: coupon.code, amount: coupon.amount })
    );
  });
  try {
    redeemTxn();
  } catch (e) {
    return res.status(500).json({ error: 'Failed to redeem coupon' });
  }
  const updated = getUserById(user.id);
  try { logger.couponRedeem({ user_code: user.unique_code, coupon_code: coupon.code, amount: coupon.amount }); } catch (e) {}
  return res.json({ success: true, new_balance: updated.balance });
});

module.exports = { router };
