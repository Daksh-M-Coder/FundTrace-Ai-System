// social.js — Friend requests, connections, unique ID lookup
const express = require('express');
const router = express.Router();
const { requireAuth } = require('./auth');
const { db, getUserById, getUserByCode, safeUser } = require('./db');
const logger = require('./logger');

// ─── SEND FRIEND REQUEST ─────────────────────────────────────────────────────

router.post('/request', requireAuth, (req, res) => {
  const { unique_code } = req.body;
  if (!unique_code) return res.status(400).json({ error: 'Unique code is required' });

  const target = getUserByCode(unique_code);
  if (!target) return res.status(404).json({ error: 'No user found with that FundTrace ID' });
  if (target.id === req.userId) return res.status(400).json({ error: 'You cannot add yourself' });
  if (target.role === 'officer') return res.status(400).json({ error: 'Cannot add bank officers' });

  // Check existing relationship
  const existing = db.prepare(
    'SELECT * FROM friends WHERE (requester_id = ? AND receiver_id = ?) OR (requester_id = ? AND receiver_id = ?)'
  ).get(req.userId, target.id, target.id, req.userId);

  if (existing) {
    if (existing.status === 'accepted') return res.status(409).json({ error: 'Already friends' });
    if (existing.status === 'pending') return res.status(409).json({ error: 'Friend request already sent' });
    if (existing.status === 'rejected') {
      // Allow re-request — update the existing row
      db.prepare('UPDATE friends SET status = ?, requester_id = ?, receiver_id = ?, updated_at = ? WHERE id = ?')
        .run('pending', req.userId, target.id, Math.floor(Date.now() / 1000), existing.id);
    }
  } else {
    db.prepare('INSERT INTO friends (requester_id, receiver_id, status) VALUES (?, ?, ?)')
      .run(req.userId, target.id, 'pending');
  }

  // Notification to target
  const sender = getUserById(req.userId);
  db.prepare(`INSERT INTO notifications (user_id, type, title, body, data) VALUES (?, 'friend_request', ?, ?, ?)`).run(
    target.id,
    'New connection request',
    `${sender.full_name} (${sender.unique_code}) wants to connect with you`,
    JSON.stringify({ from_id: req.userId, from_name: sender.full_name, from_code: sender.unique_code })
  );
  try { logger.friendRequest({ from_code: sender.unique_code, to_code: target.unique_code, status: 'sent' }); } catch (e) {}

  // Real-time notification
  const io = req.app.get('io');
  if (io) {
    io.to(`user_${target.id}`).emit('friend_request', {
      from_name: sender.full_name,
      from_code: sender.unique_code
    });
  }

  return res.json({ success: true, message: `Connection request sent to ${target.full_name}` });
});

// ─── RESPOND TO REQUEST ──────────────────────────────────────────────────────

router.post('/respond', requireAuth, (req, res) => {
  const { request_id, action } = req.body; // action: 'accept' | 'reject'
  if (!request_id || !['accept', 'reject'].includes(action)) {
    return res.status(400).json({ error: 'request_id and action (accept/reject) required' });
  }

  const request = db.prepare(
    'SELECT * FROM friends WHERE id = ? AND receiver_id = ? AND status = ?'
  ).get(request_id, req.userId, 'pending');

  if (!request) return res.status(404).json({ error: 'Request not found' });

  const newStatus = action === 'accept' ? 'accepted' : 'rejected';
  db.prepare('UPDATE friends SET status = ?, updated_at = ? WHERE id = ?')
    .run(newStatus, Math.floor(Date.now() / 1000), request_id);

  if (action === 'accept') {
    const accepter = getUserById(req.userId);
    const requester = getUserById(request.requester_id);

    // Notify requester
    db.prepare(`INSERT INTO notifications (user_id, type, title, body, data) VALUES (?, 'friend_accepted', ?, ?, ?)`).run(
      request.requester_id,
      'Connection accepted!',
      `${accepter.full_name} accepted your connection request`,
      JSON.stringify({ user_id: req.userId, name: accepter.full_name, code: accepter.unique_code })
    );

    const io = req.app.get('io');
    if (io) {
      io.to(`user_${request.requester_id}`).emit('friend_accepted', {
        name: accepter.full_name,
        code: accepter.unique_code
      });
    }
    try { logger.friendRequest({ from_code: requester.unique_code, to_code: accepter.unique_code, status: 'accepted' }); } catch (e) {}
  }

  return res.json({ success: true, status: newStatus });
});

// ─── GET FRIENDS LIST ────────────────────────────────────────────────────────

router.get('/list', requireAuth, (req, res) => {
  const friends = db.prepare(`
    SELECT
      f.id, f.status, f.created_at, f.updated_at,
      CASE WHEN f.requester_id = ? THEN f.receiver_id ELSE f.requester_id END AS friend_id,
      u.full_name, u.unique_code, u.account_number, u.branch, u.account_type, u.status AS account_status
    FROM friends f
    JOIN users u ON u.id = (CASE WHEN f.requester_id = ? THEN f.receiver_id ELSE f.requester_id END)
    WHERE (f.requester_id = ? OR f.receiver_id = ?) AND f.status = 'accepted'
    ORDER BY u.full_name ASC
  `).all(req.userId, req.userId, req.userId, req.userId);

  return res.json({ friends });
});

// ─── GET PENDING REQUESTS ────────────────────────────────────────────────────

router.get('/requests', requireAuth, (req, res) => {
  // Incoming requests
  const incoming = db.prepare(`
    SELECT f.id, f.created_at, u.full_name, u.unique_code, u.account_number
    FROM friends f
    JOIN users u ON u.id = f.requester_id
    WHERE f.receiver_id = ? AND f.status = 'pending'
    ORDER BY f.created_at DESC
  `).all(req.userId);

  // Outgoing requests
  const outgoing = db.prepare(`
    SELECT f.id, f.created_at, u.full_name, u.unique_code, u.account_number
    FROM friends f
    JOIN users u ON u.id = f.receiver_id
    WHERE f.requester_id = ? AND f.status = 'pending'
    ORDER BY f.created_at DESC
  `).all(req.userId);

  return res.json({ incoming, outgoing });
});

// ─── REMOVE FRIEND ───────────────────────────────────────────────────────────

router.delete('/remove/:friendId', requireAuth, (req, res) => {
  const { friendId } = req.params;
  db.prepare(
    'DELETE FROM friends WHERE ((requester_id = ? AND receiver_id = ?) OR (requester_id = ? AND receiver_id = ?)) AND status = ?'
  ).run(req.userId, friendId, friendId, req.userId, 'accepted');
  return res.json({ success: true });
});

// ─── SEARCH USERS ────────────────────────────────────────────────────────────

router.get('/search', requireAuth, (req, res) => {
  const { q } = req.query;
  if (!q || q.trim().length < 2) return res.status(400).json({ error: 'Query too short' });

  const results = db.prepare(`
    SELECT id, full_name, unique_code, account_number, branch
    FROM users
    WHERE role = 'client' AND id != ?
      AND (full_name LIKE ? OR unique_code LIKE ? OR account_number LIKE ?)
    LIMIT 10
  `).all(req.userId, `%${q}%`, `%${q.toUpperCase()}%`, `%${q.toUpperCase()}%`);

  return res.json({ results });
});

module.exports = router;
