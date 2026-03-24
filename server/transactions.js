// transactions.js — Money transfers, history, balance, fraud pre-check
const express = require('express');
const router = express.Router();
const { requireAuth, requireOfficer } = require('./auth');
const logger = require('./logger');
const { db, getUserById, getUserByAccount, getUserByCode, generateTxnId, safeUser } = require('./db');
const { scoreFraud, createFraudAlert } = require('./fraud');

// ─── GET BALANCE & ACCOUNT INFO ──────────────────────────────────────────────

router.get('/account', requireAuth, (req, res) => {
  const user = getUserById(req.userId);
  if (!user) return res.status(404).json({ error: 'User not found' });
  return res.json({ user: safeUser(user) });
});

// ─── GET TRANSACTION HISTORY ─────────────────────────────────────────────────

router.get('/history', requireAuth, (req, res) => {
  const { limit = 50, offset = 0 } = req.query;
  const user = getUserById(req.userId);

  const txns = db.prepare(`
    SELECT
      t.*,
      sender.full_name   AS sender_name,
      sender.unique_code AS sender_code,
      receiver.full_name AS receiver_name,
      receiver.unique_code AS receiver_code
    FROM transactions t
    LEFT JOIN users sender   ON t.from_user_id = sender.id
    LEFT JOIN users receiver ON t.to_user_id   = receiver.id
    WHERE t.from_user_id = ? OR t.to_user_id = ?
    ORDER BY t.created_at DESC
    LIMIT ? OFFSET ?
  `).all(req.userId, req.userId, parseInt(limit), parseInt(offset));

  const total = db.prepare(
    'SELECT COUNT(*) as cnt FROM transactions WHERE from_user_id = ? OR to_user_id = ?'
  ).get(req.userId, req.userId);

  return res.json({ transactions: txns, total: total.cnt, balance: user.balance });
});

// ─── LOOKUP USER (for sending money — by code or account number) ─────────────

router.get('/lookup', requireAuth, (req, res) => {
  const { query } = req.query;
  if (!query || query.trim().length < 3) {
    return res.status(400).json({ error: 'Query too short' });
  }

  const q = query.trim().toUpperCase();
  let target = null;

  if (q.startsWith('FT-')) {
    target = db.prepare("SELECT id, full_name, unique_code, account_number, branch, account_type FROM users WHERE unique_code = ? AND role = 'client'").get(q);
  } else if (q.startsWith('ACC-')) {
    target = db.prepare("SELECT id, full_name, unique_code, account_number, branch, account_type FROM users WHERE account_number = ? AND role = 'client'").get(q);
  } else {
    // Search by name (partial)
    target = db.prepare("SELECT id, full_name, unique_code, account_number, branch, account_type FROM users WHERE full_name LIKE ? AND role = 'client' LIMIT 5").all(`%${query.trim()}%`);
    return res.json({ results: target });
  }

  if (!target) return res.status(404).json({ error: 'No account found with that ID' });
  if (target.id === req.userId) return res.status(400).json({ error: 'Cannot send money to yourself' });

  return res.json({ user: target });
});

// ─── SEND MONEY ──────────────────────────────────────────────────────────────

router.post('/send', requireAuth, (req, res) => {
  const { to_code, to_account, amount, note, channel = 'IMPS' } = req.body;

  // Validate amount
  const amt = parseFloat(amount);
  if (isNaN(amt) || amt <= 0) return res.status(400).json({ error: 'Invalid amount' });
  if (amt > 1000000) return res.status(400).json({ error: 'Amount exceeds single transaction limit of ₹10,00,000' });
  if (amt < 1) return res.status(400).json({ error: 'Minimum transfer amount is ₹1' });

  const sender = getUserById(req.userId);
  if (!sender) return res.status(404).json({ error: 'Sender not found' });
  if (sender.status === 'frozen') return res.status(403).json({ error: 'Your account is frozen. Contact support.' });

  // Find receiver
  let receiver = null;
  if (to_code) receiver = getUserByCode(to_code);
  else if (to_account) receiver = getUserByAccount(to_account);
  if (!receiver) return res.status(404).json({ error: 'Recipient account not found' });
  if (receiver.id === sender.id) return res.status(400).json({ error: 'Cannot send money to yourself' });
  if (receiver.status === 'frozen') return res.status(400).json({ error: 'Recipient account is frozen' });

  // Balance check
  if (sender.balance < amt) {
    return res.status(400).json({
      error: `Insufficient balance. Available: ₹${sender.balance.toFixed(2)}`
    });
  }

  // Validate channel
  const validChannels = ['IMPS', 'NEFT', 'RTGS', 'UPI'];
  const txnChannel = validChannels.includes(channel) ? channel : 'IMPS';

  // Execute transaction atomically
  const txnId = generateTxnId();

  const doTransaction = db.transaction(() => {
    // Debit sender
    db.prepare('UPDATE users SET balance = balance - ? WHERE id = ? AND balance >= ?')
      .run(amt, sender.id, amt);

    // Verify debit happened
    const updatedSender = getUserById(sender.id);
    if (updatedSender.balance > sender.balance - amt + 0.001) {
      throw new Error('Debit failed — balance check failed');
    }

    // Credit receiver
    db.prepare('UPDATE users SET balance = balance + ? WHERE id = ?')
      .run(amt, receiver.id);

    // Record transaction
    const result = db.prepare(`
      INSERT INTO transactions (txn_id, from_user_id, to_user_id, from_account, to_account, amount, channel, note, status)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed')
    `).run(txnId, sender.id, receiver.id, sender.account_number, receiver.account_number, amt, txnChannel, note || null);

    return result.lastInsertRowid;
  });

  let txnRowId;
  try {
    txnRowId = doTransaction();
  } catch (err) {
    console.error('Transaction failed:', err);
    return res.status(500).json({ error: 'Transaction processing failed. Please try again.' });
  }

  // Fraud scoring (async — don't block the response)
  const txn = db.prepare('SELECT * FROM transactions WHERE id = ?').get(txnRowId);
  scoreFraud(txn, sender, receiver).then(({ score, patterns }) => {
    if (score > 0) {
      db.prepare('UPDATE transactions SET fraud_score = ?, flagged = ? WHERE id = ?')
        .run(score, score > 50 ? 1 : 0, txnRowId);

      if (score > 50) {
        createFraudAlert(txn, sender, receiver, score, patterns);
      }
    }
    try {
      logger.transaction({
        txn_id: txn.txn_id,
        from_code: sender.unique_code,
        to_code: receiver.unique_code,
        from_name: sender.full_name,
        to_name: receiver.full_name,
        amount: txn.amount,
        channel: txn.channel,
        note: txn.note,
        fraud_score: score || 0,
        flagged: score > 50,
        status: txn.status
      });
    } catch (e) {}
  }).catch(console.error);

  // Notifications
  db.prepare(`INSERT INTO notifications (user_id, type, title, body, data) VALUES (?, 'txn_sent', ?, ?, ?)`).run(
    sender.id,
    `Money sent: ₹${amt.toFixed(2)}`,
    `You sent ₹${amt.toFixed(2)} to ${receiver.full_name} via ${txnChannel}${note ? ' — ' + note : ''}`,
    JSON.stringify({ txn_id: txnId, amount: amt, to: receiver.full_name })
  );

  db.prepare(`INSERT INTO notifications (user_id, type, title, body, data) VALUES (?, 'txn_received', ?, ?, ?)`).run(
    receiver.id,
    `Money received: ₹${amt.toFixed(2)}`,
    `You received ₹${amt.toFixed(2)} from ${sender.full_name} via ${txnChannel}${note ? ' — ' + note : ''}`,
    JSON.stringify({ txn_id: txnId, amount: amt, from: sender.full_name })
  );

  // Emit real-time events via Socket.IO (attached to app in index.js)
  const io = req.app.get('io');
  if (io) {
    // Notify recipient live
    io.to(`user_${receiver.id}`).emit('transaction_received', {
      txn_id: txnId,
      amount: amt,
      from: sender.full_name,
      from_code: sender.unique_code,
      channel: txnChannel,
      note: note || null,
      timestamp: Date.now()
    });

    // Notify officer dashboard
    io.to('officers').emit('new_transaction', {
      txn_id: txnId,
      from_name: sender.full_name,
      to_name: receiver.full_name,
      amount: amt,
      channel: txnChannel,
      timestamp: Date.now()
    });
  }

  return res.json({
    success: true,
    txn_id: txnId,
    amount: amt,
    to: receiver.full_name,
    new_balance: getUserById(sender.id).balance
  });
});

// ─── GET SINGLE TRANSACTION ──────────────────────────────────────────────────

router.get('/:txnId', requireAuth, (req, res) => {
  const txn = db.prepare(`
    SELECT t.*,
      s.full_name AS sender_name, s.unique_code AS sender_code,
      r.full_name AS receiver_name, r.unique_code AS receiver_code
    FROM transactions t
    LEFT JOIN users s ON t.from_user_id = s.id
    LEFT JOIN users r ON t.to_user_id = r.id
    WHERE t.txn_id = ? AND (t.from_user_id = ? OR t.to_user_id = ?)
  `).get(req.params.txnId, req.userId, req.userId);

  if (!txn) return res.status(404).json({ error: 'Transaction not found' });
  return res.json({ transaction: txn });
});

// ─── NOTIFICATIONS ───────────────────────────────────────────────────────────

router.get('/notifications/all', requireAuth, (req, res) => {
  const notifs = db.prepare(
    'SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50'
  ).all(req.userId);
  const unread = db.prepare('SELECT COUNT(*) as cnt FROM notifications WHERE user_id = ? AND read = 0').get(req.userId);
  return res.json({ notifications: notifs, unread: unread.cnt });
});

router.post('/notifications/read', requireAuth, (req, res) => {
  db.prepare('UPDATE notifications SET read = 1 WHERE user_id = ?').run(req.userId);
  return res.json({ success: true });
});


// ─── OFFICER: LIST ALL TRANSACTIONS (across all accounts) ────────────────────
// GET /api/transactions/officer/list
// Query params: account_code, channel, status, sort (amount_desc|amount_asc|date_desc|date_asc), limit, offset

router.get('/officer/list', requireOfficer, (req, res) => {
  const { account_code, channel, status, sort = 'date_desc', limit = 50, offset = 0 } = req.query;

  let where = [];
  let params = [];

  if (account_code) {
    const user = db.prepare("SELECT id FROM users WHERE UPPER(unique_code)=UPPER(?) LIMIT 1").get(account_code.trim());
    if (!user) return res.status(404).json({ error: `Account ${account_code} not found` });
    where.push('(t.from_user_id = ? OR t.to_user_id = ?)');
    params.push(user.id, user.id);
  }
  if (channel) { where.push('t.channel = ?'); params.push(channel.toUpperCase()); }
  if (status)  { where.push('t.status = ?');  params.push(status.toLowerCase()); }

  const orderMap = {
    amount_desc: 't.amount DESC',
    amount_asc:  't.amount ASC',
    date_desc:   't.created_at DESC',
    date_asc:    't.created_at ASC'
  };
  const orderBy = orderMap[sort] || 't.created_at DESC';
  const whereClause = where.length ? 'WHERE ' + where.join(' AND ') : '';

  const rows = db.prepare(`
    SELECT
      t.txn_id, t.amount, t.channel, t.status, t.fraud_score, t.flagged, t.note,
      datetime(t.created_at, 'unixepoch') AS txn_date, t.created_at AS ts,
      s.full_name  AS sender_name,  s.unique_code  AS sender_code,
      s.account_number AS sender_account,
      r.full_name  AS receiver_name, r.unique_code  AS receiver_code,
      r.account_number AS receiver_account
    FROM transactions t
    LEFT JOIN users s ON t.from_user_id  = s.id
    LEFT JOIN users r ON t.to_user_id    = r.id
    ${whereClause}
    ORDER BY ${orderBy}
    LIMIT ? OFFSET ?
  `).all(...params, parseInt(limit), parseInt(offset));

  const countRow = db.prepare(
    `SELECT COUNT(*) AS cnt FROM transactions t ${whereClause}`
  ).get(...params);

  // All accounts for the selector dropdown
  const accounts = db.prepare(
    "SELECT unique_code, full_name, balance FROM users WHERE role='client' ORDER BY full_name ASC"
  ).all();

  // Channel + status breakdown (for summary bar)
  const channels = db.prepare(
    `SELECT channel, COUNT(*) as cnt, ROUND(SUM(amount),2) as vol FROM transactions t ${whereClause} GROUP BY channel`
  ).all(...params);

  return res.json({
    transactions: rows,
    total: countRow.cnt,
    accounts,
    channels,
    filters: { account_code: account_code || null, channel: channel || null, status: status || null, sort }
  });
});

// ─── OFFICER: EXPORT TRANSACTIONS (CSV or JSON) ───────────────────────────────
// GET /api/transactions/officer/export?account_code=FT-XXXXX&format=csv|json

router.get('/officer/export', requireOfficer, (req, res) => {
  const { account_code, format = 'csv' } = req.query;

  let where = [];
  let params = [];

  if (account_code) {
    const user = db.prepare("SELECT id FROM users WHERE UPPER(unique_code)=UPPER(?) LIMIT 1").get((account_code || '').trim());
    if (!user) return res.status(404).json({ error: `Account ${account_code} not found` });
    where.push('(t.from_user_id = ? OR t.to_user_id = ?)');
    params.push(user.id, user.id);
  }

  const whereClause = where.length ? 'WHERE ' + where.join(' AND ') : '';
  const rows = db.prepare(`
    SELECT
      t.txn_id, t.amount, t.channel, t.status, t.fraud_score, t.flagged, t.note,
      datetime(t.created_at, 'unixepoch') AS txn_date,
      s.full_name AS sender_name, s.unique_code AS sender_code, s.account_number AS sender_account,
      r.full_name AS receiver_name, r.unique_code AS receiver_code, r.account_number AS receiver_account
    FROM transactions t
    LEFT JOIN users s ON t.from_user_id = s.id
    LEFT JOIN users r ON t.to_user_id   = r.id
    ${whereClause}
    ORDER BY t.created_at DESC
  `).all(...params);

  const tag = account_code ? `_${account_code}` : '_all';
  const filename = `fundtrace_transactions${tag}_${new Date().toISOString().slice(0,10)}`;

  if (format === 'json') {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}.json"`);
    return res.json({ exported_at: new Date().toISOString(), count: rows.length, transactions: rows });
  }

  // CSV export
  const cols = ['txn_id','txn_date','sender_name','sender_code','sender_account',
                 'receiver_name','receiver_code','receiver_account','amount','channel',
                 'status','fraud_score','flagged','note'];
  const escape = v => {
    if (v == null) return '';
    const s = String(v);
    return s.includes(',') || s.includes('"') || s.includes('\n') ? `"${s.replace(/"/g,'""')}"` : s;
  };
  const csvLines = [cols.join(',')];
  for (const row of rows) {
    csvLines.push(cols.map(c => escape(row[c])).join(','));
  }
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', `attachment; filename="${filename}.csv"`);
  return res.send(csvLines.join('\r\n'));
});

module.exports = router;

