// fraud.js — Fraud pattern detection engine (rule-based ML simulation)
const { db, generateAlertId } = require('./db');
const logger = require('./logger');

// ─── FRAUD SCORING ENGINE ────────────────────────────────────────────────────
// Simulates a GNN + Isolation Forest ensemble model
// Returns a risk score 0–100 and list of triggered patterns

async function scoreFraud(txn, sender, receiver) {
  const patterns = [];
  let score = 0;

  const now = Math.floor(Date.now() / 1000);
  const window1h = now - 3600;       // 1 hour
  const window24h = now - 86400;     // 24 hours
  const window72h = now - 259200;    // 72 hours

  // ── 1. RAPID LAYERING — many txns from same account in 1 hour ────────────
  const recentSent = db.prepare(
    'SELECT COUNT(*) as cnt, SUM(amount) as total FROM transactions WHERE from_user_id = ? AND created_at > ? AND status = ?'
  ).get(sender.id, window1h, 'completed');

  if (recentSent.cnt >= 5) {
    const severity = recentSent.cnt >= 10 ? 30 : 15;
    score += severity;
    patterns.push({
      type: 'layering',
      desc: `${recentSent.cnt} outgoing transactions in last hour totalling ₹${(recentSent.total || 0).toFixed(2)}`,
      severity
    });
  }

  // ── 2. CIRCULAR TRANSACTION DETECTION ───────────────────────────────────
  // Check if money has flowed: sender -> X -> ... -> receiver -> sender (within 72h)
  const recentReceivedBySender = db.prepare(
    'SELECT from_user_id FROM transactions WHERE to_user_id = ? AND created_at > ? AND status = ?'
  ).all(sender.id, window72h, 'completed').map(r => r.from_user_id);

  const recentSentToByReceiver = db.prepare(
    'SELECT to_user_id FROM transactions WHERE from_user_id = ? AND created_at > ? AND status = ?'
  ).all(receiver.id, window72h, 'completed').map(r => r.to_user_id);

  // Overlap = potential circular flow
  const circularOverlap = recentReceivedBySender.filter(id => recentSentToByReceiver.includes(id));
  if (circularOverlap.length > 0) {
    score += 35;
    patterns.push({
      type: 'circular',
      desc: `Potential circular transaction detected — funds may be returning to origin via ${circularOverlap.length} intermediate account(s)`,
      severity: 35
    });
  }

  // Direct round-trip: A->B then B->A within 24h
  const directRoundTrip = db.prepare(
    'SELECT id FROM transactions WHERE from_user_id = ? AND to_user_id = ? AND created_at > ? AND status = ?'
  ).get(receiver.id, sender.id, window24h, 'completed');
  if (directRoundTrip) {
    score += 25;
    patterns.push({
      type: 'circular',
      desc: 'Direct round-trip: money returned from recipient to sender within 24 hours',
      severity: 25
    });
  }

  // ── 3. STRUCTURING BELOW THRESHOLD ──────────────────────────────────────
  // Multiple transactions just below ₹10 lakh (₹1,000,000) reporting threshold
  const threshold = 900000; // ₹9 lakh
  if (txn.amount >= threshold && txn.amount < 1000000) {
    const similarRecent = db.prepare(
      'SELECT COUNT(*) as cnt FROM transactions WHERE from_user_id = ? AND amount >= ? AND amount < 1000000 AND created_at > ?'
    ).get(sender.id, threshold, window24h);

    if (similarRecent.cnt >= 2) {
      score += 30;
      patterns.push({
        type: 'structuring',
        desc: `${similarRecent.cnt} transactions between ₹9–10L in 24 hours — possible structuring to avoid reporting threshold`,
        severity: 30
      });
    }
  }

  // ── 4. DORMANT ACCOUNT SUDDEN HIGH-VALUE TRANSFER ───────────────────────
  const thirtyDaysAgo = now - 30 * 86400;
  const senderLastTxn = db.prepare(
    'SELECT created_at FROM transactions WHERE from_user_id = ? ORDER BY created_at DESC LIMIT 1'
  ).get(sender.id);

  // No prior transactions, or last txn was >30 days ago, and now doing high value
  if (txn.amount > 50000 && (!senderLastTxn || senderLastTxn.created_at < thirtyDaysAgo)) {
    score += 20;
    patterns.push({
      type: 'dormant',
      desc: `Account was dormant (no activity for ${senderLastTxn ? '30+' : 'indefinite'} days) and is now initiating high-value transfer of ₹${txn.amount.toFixed(2)}`,
      severity: 20
    });
  }

  // ── 5. PROFILE MISMATCH — balance spike ──────────────────────────────────
  // Sender balance was very low, but suddenly received large amount and is now sending it
  const senderBalanceBefore = sender.balance + txn.amount; // before this txn
  if (senderBalanceBefore > sender.balance * 5 && senderBalanceBefore > 100000) {
    score += 15;
    patterns.push({
      type: 'profile_mismatch',
      desc: `Balance increased 5× recently (₹${sender.balance.toFixed(2)} current). Possible pass-through account behaviour.`,
      severity: 15
    });
  }

  // ── 6. HIGH VELOCITY — receiver getting many inflows ────────────────────
  const receiverInflows = db.prepare(
    'SELECT COUNT(*) as cnt FROM transactions WHERE to_user_id = ? AND created_at > ?'
  ).get(receiver.id, window1h);

  if (receiverInflows.cnt >= 8) {
    score += 20;
    patterns.push({
      type: 'layering',
      desc: `Recipient received ${receiverInflows.cnt} inbound transfers in the last hour — possible aggregation point`,
      severity: 20
    });
  }

  // Cap at 100
  score = Math.min(score, 100);

  return { score, patterns };
}

// ─── CREATE FRAUD ALERT ──────────────────────────────────────────────────────

function createFraudAlert(txn, sender, receiver, score, patterns) {
  const alertId = generateAlertId();
  const primaryPattern = patterns.sort((a, b) => b.severity - a.severity)[0];

  try {
    db.prepare(`
      INSERT INTO fraud_alerts (alert_id, transaction_id, user_id, pattern_type, risk_score, description, status)
      VALUES (?, ?, ?, ?, ?, ?, 'open')
    `).run(
      alertId,
      txn.id,
      sender.id,
      primaryPattern.type,
      score,
      JSON.stringify({
        patterns,
        txn_id: txn.txn_id,
        sender: { id: sender.id, name: sender.full_name, code: sender.unique_code },
        receiver: { id: receiver.id, name: receiver.full_name, code: receiver.unique_code },
        amount: txn.amount,
        channel: txn.channel
      })
    );

    // Emit real-time fraud alert to officer dashboard
    // (io is set on the module after index.js initialises it)
    if (module.exports._io) {
      module.exports._io.to('officers').emit('fraud_alert', {
        alert_id: alertId,
        risk_score: score,
        pattern: primaryPattern.type,
        amount: txn.amount,
        sender_name: sender.full_name,
        receiver_name: receiver.full_name,
        timestamp: Date.now()
      });
    }
    try {
      logger.fraudAlert({
        alert_id: alertId,
        pattern_type: primaryPattern.type,
        risk_score: score,
        user_code: sender.unique_code,
        user_name: sender.full_name,
        txn_id: txn.txn_id,
        amount: txn.amount,
        description: `Primary: ${primaryPattern.type}`
      });
    } catch (e) {}

    console.log(`🚨 Fraud alert created: ${alertId} (score: ${score}) — ${primaryPattern.type}`);
  } catch (err) {
    console.error('Failed to create fraud alert:', err);
  }

  return alertId;
}

// ─── OFFICER ROUTES ──────────────────────────────────────────────────────────

const express = require('express');
const router = express.Router();
const { requireOfficer, requireAuth } = require('./auth');

// GET all fraud alerts (officer only)
router.get('/alerts', requireOfficer, (req, res) => {
  const { status, limit = 50, offset = 0 } = req.query;

  let query = `
    SELECT fa.*,
      u.full_name AS subject_name, u.unique_code, u.account_number, u.branch,
      t.txn_id, t.amount, t.channel, t.from_account, t.to_account
    FROM fraud_alerts fa
    LEFT JOIN users u ON fa.user_id = u.id
    LEFT JOIN transactions t ON fa.transaction_id = t.id
  `;
  const params = [];
  if (status) { query += ' WHERE fa.status = ?'; params.push(status); }
  query += ' ORDER BY fa.created_at DESC LIMIT ? OFFSET ?';
  params.push(parseInt(limit), parseInt(offset));

  const alerts = db.prepare(query).all(...params);
  const total = db.prepare(`SELECT COUNT(*) as cnt FROM fraud_alerts${status ? ' WHERE status = ?' : ''}`).get(...(status ? [status] : []));

  return res.json({ alerts, total: total.cnt });
});

// GET single alert detail
router.get('/alerts/:alertId', requireOfficer, (req, res) => {
  const alert = db.prepare(`
    SELECT fa.*,
      u.full_name, u.unique_code, u.account_number, u.branch, u.balance, u.status AS account_status,
      t.txn_id, t.amount, t.channel, t.from_account, t.to_account, t.created_at AS txn_time
    FROM fraud_alerts fa
    LEFT JOIN users u ON fa.user_id = u.id
    LEFT JOIN transactions t ON fa.transaction_id = t.id
    WHERE fa.alert_id = ?
  `).get(req.params.alertId);

  if (!alert) return res.status(404).json({ error: 'Alert not found' });

  // Get full transaction chain for this user
  const chain = db.prepare(`
    SELECT t.*,
      s.full_name AS sender_name, s.unique_code AS sender_code,
      r.full_name AS receiver_name, r.unique_code AS receiver_code
    FROM transactions t
    LEFT JOIN users s ON t.from_user_id = s.id
    LEFT JOIN users r ON t.to_user_id = r.id
    WHERE t.from_user_id = ? OR t.to_user_id = ?
    ORDER BY t.created_at DESC LIMIT 30
  `).all(alert.user_id, alert.user_id);

  return res.json({ alert, chain });
});

// PATCH update alert status
router.patch('/alerts/:alertId', requireOfficer, (req, res) => {
  const { status } = req.body;
  const validStatuses = ['open', 'reviewing', 'closed', 'filed'];
  if (!validStatuses.includes(status)) return res.status(400).json({ error: 'Invalid status' });

  db.prepare('UPDATE fraud_alerts SET status = ?, updated_at = ? WHERE alert_id = ?')
    .run(status, Math.floor(Date.now() / 1000), req.params.alertId);

  return res.json({ success: true });
});

// POST freeze an account (officer only)
router.post('/freeze/:userId', requireOfficer, (req, res) => {
  const { reason } = req.body;
  db.prepare('UPDATE users SET status = ? WHERE id = ?').run('frozen', req.params.userId);

  db.prepare(`INSERT INTO notifications (user_id, type, title, body) VALUES (?, 'system', ?, ?)`).run(
    req.params.userId,
    'Account Frozen',
    `Your account has been temporarily frozen by the bank. Please contact support. ${reason ? 'Reason: ' + reason : ''}`
  );
  try {
    const u = db.prepare('SELECT unique_code FROM users WHERE id = ?').get(req.params.userId);
    logger.accountStatusChange({ user_code: u?.unique_code, new_status: 'frozen', reason: reason || null, officer_code: 'FT-OFFICER' });
    logger.officerAction({ action: 'freeze', target_id: req.params.userId, target_code: u?.unique_code, officer_code: 'FT-OFFICER', notes: reason || null });
  } catch (e) {}

  return res.json({ success: true });
});

// POST unfreeze account
router.post('/unfreeze/:userId', requireOfficer, (req, res) => {
  db.prepare('UPDATE users SET status = ? WHERE id = ?').run('active', req.params.userId);
  try {
    const u = db.prepare('SELECT unique_code FROM users WHERE id = ?').get(req.params.userId);
    logger.accountStatusChange({ user_code: u?.unique_code, new_status: 'active', officer_code: 'FT-OFFICER' });
    logger.officerAction({ action: 'unfreeze', target_id: req.params.userId, target_code: u?.unique_code, officer_code: 'FT-OFFICER' });
  } catch (e) {}
  return res.json({ success: true });
});

// GET all accounts (officer view)
router.get('/accounts', requireOfficer, (req, res) => {
  const { status, limit = 100, offset = 0 } = req.query;
  let q = `SELECT id, unique_code, full_name, email, phone, role, balance, account_number, branch, account_type, status, last_active, created_at FROM users WHERE role = 'client'`;
  const params = [];
  if (status) { q += ' AND status = ?'; params.push(status); }
  q += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
  params.push(parseInt(limit), parseInt(offset));

  const accounts = db.prepare(q).all(...params);
  const total = db.prepare(`SELECT COUNT(*) as cnt FROM users WHERE role = 'client'${status ? ' AND status = ?' : ''}`).get(...(status ? [status] : []));

  return res.json({ accounts, total: total.cnt });
});

// GET fund flow graph for a specific user (for graph explorer)
router.get('/graph/:userId', requireOfficer, (req, res) => {
  const userId = parseInt(req.params.userId);
  const depth = parseInt(req.query.depth || 2);
  const window = parseInt(req.query.window || 30) * 86400; // days to seconds
  const since = Math.floor(Date.now() / 1000) - window;

  // BFS to build graph up to `depth` hops
  const visited = new Set([userId]);
  const nodes = new Map();
  const edges = [];
  const queue = [{ id: userId, hop: 0 }];

  while (queue.length > 0) {
    const { id, hop } = queue.shift();
    const user = db.prepare('SELECT id, full_name, unique_code, account_number, balance, status, branch FROM users WHERE id = ?').get(id);
    if (!user) continue;

    const txnCount = db.prepare('SELECT COUNT(*) as cnt FROM transactions WHERE (from_user_id = ? OR to_user_id = ?) AND created_at > ?').get(id, id, since);
    const fraudScore = db.prepare('SELECT MAX(risk_score) as score FROM fraud_alerts WHERE user_id = ?').get(id);

    nodes.set(id, {
      id,
      label: user.account_number,
      name: user.full_name,
      code: user.unique_code,
      balance: user.balance,
      status: user.status,
      branch: user.branch,
      txn_count: txnCount.cnt,
      risk_score: fraudScore?.score || 0
    });

    if (hop < depth) {
      const connected = db.prepare(`
        SELECT DISTINCT
          CASE WHEN from_user_id = ? THEN to_user_id ELSE from_user_id END AS connected_id,
          SUM(amount) as total_flow,
          COUNT(*) as txn_count,
          MAX(flagged) as has_flag
        FROM transactions
        WHERE (from_user_id = ? OR to_user_id = ?) AND created_at > ?
        GROUP BY connected_id
      `).all(id, id, id, since);

      for (const conn of connected) {
        edges.push({
          from: id,
          to: conn.connected_id,
          amount: conn.total_flow,
          txn_count: conn.txn_count,
          suspicious: conn.has_flag === 1
        });
        if (!visited.has(conn.connected_id)) {
          visited.add(conn.connected_id);
          queue.push({ id: conn.connected_id, hop: hop + 1 });
        }
      }
    }
  }

  return res.json({ nodes: Array.from(nodes.values()), edges });
});

// GET dashboard summary stats
router.get('/stats', requireOfficer, (req, res) => {
  const totalAccounts = db.prepare("SELECT COUNT(*) as cnt FROM users WHERE role = 'client'").get();
  const frozenAccounts = db.prepare("SELECT COUNT(*) as cnt FROM users WHERE status = 'frozen'").get();
  const totalTxns = db.prepare("SELECT COUNT(*) as cnt, SUM(amount) as vol FROM transactions WHERE status = 'completed'").get();
  const alertStats = db.prepare("SELECT status, COUNT(*) as cnt FROM fraud_alerts GROUP BY status").all();
  const highRisk = db.prepare("SELECT COUNT(*) as cnt FROM fraud_alerts WHERE risk_score >= 70 AND status = 'open'").get();
  const recentTxns = db.prepare(`
    SELECT t.*, s.full_name AS sender_name, r.full_name AS receiver_name
    FROM transactions t
    LEFT JOIN users s ON t.from_user_id = s.id
    LEFT JOIN users r ON t.to_user_id = r.id
    ORDER BY t.created_at DESC LIMIT 20
  `).all();
  const patternBreakdown = db.prepare("SELECT pattern_type, COUNT(*) as cnt FROM fraud_alerts GROUP BY pattern_type").all();

  return res.json({
    total_accounts: totalAccounts.cnt,
    frozen_accounts: frozenAccounts.cnt,
    total_transactions: totalTxns.cnt,
    total_volume: totalTxns.vol || 0,
    alert_stats: alertStats,
    high_risk_open: highRisk.cnt,
    recent_transactions: recentTxns,
    pattern_breakdown: patternBreakdown
  });
});

module.exports = { router, scoreFraud, createFraudAlert };
