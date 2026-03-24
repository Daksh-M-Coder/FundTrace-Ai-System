// logger.js — Structured JSONL Event Logger for FraudSense AI
// =============================================================
// Drop this into server/ and require it in any route file.
// Every meaningful event gets written to ai/logs/events.jsonl
// in a clean, LLM-readable format.
//
// Usage:
//   const logger = require('./logger');
//   logger.transaction({ from_code, to_code, amount, channel, ... });
//   logger.fraudAlert({ alert_id, pattern, risk_score, ... });
//   logger.login({ user_code, status });

const fs = require('fs');
const path = require('path');

const LOG_FILE = path.join(__dirname, '..', 'ai', 'logs', 'events.jsonl');
const MAX_FILE_SIZE_MB = 50; // Rotate after 50MB

// Ensure log directory exists
function ensureLogDir() {
  const dir = path.dirname(LOG_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

// Write one event to the log file
function writeEvent(event_type, entity_id, entity_type, data) {
  ensureLogDir();

  // Rotate if too large
  try {
    const stats = fs.statSync(LOG_FILE);
    if (stats.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      const rotated = LOG_FILE.replace('.jsonl', `_${Date.now()}.jsonl`);
      fs.renameSync(LOG_FILE, rotated);
    }
  } catch (e) { /* file doesn't exist yet */ }

  const entry = {
    ts: new Date().toISOString(),
    event: event_type,
    entity_id: entity_id || null,
    entity_type: entity_type || null,
    source: 'fundtrace-server',
    data: data || {}
  };

  try {
    fs.appendFileSync(LOG_FILE, JSON.stringify(entry) + '\n', 'utf8');
  } catch (e) {
    console.error('[Logger] Failed to write event:', e.message);
  }
}

// ─── EVENT WRITERS ───────────────────────────────────────────────────────────

const logger = {

  // Transaction completed (sent or received)
  transaction(data) {
    const {
      txn_id, from_code, to_code, from_name, to_name,
      amount, channel, note, fraud_score, flagged, status
    } = data;
    writeEvent('transaction', from_code, 'account', {
      txn_id,
      from_code, from_name,
      to_code, to_name,
      amount,
      channel,
      note: note || null,
      fraud_score: Math.round(fraud_score || 0),
      flagged: !!flagged,
      status
    });
  },

  // Fraud alert created
  fraudAlert(data) {
    const {
      alert_id, pattern_type, risk_score, user_code, user_name,
      txn_id, amount, description
    } = data;
    writeEvent('fraud_alert', user_code, 'account', {
      alert_id,
      pattern: pattern_type,
      risk_score: Math.round(risk_score || 0),
      user_code, user_name,
      txn_id, amount,
      description: typeof description === 'string' ? description.substring(0, 200) : null
    });
  },

  // User login (success or failure)
  login(data) {
    const { user_code, user_name, status, ip } = data;
    writeEvent('login', user_code, 'user', {
      user_code, user_name,
      status, // 'success' | 'failed' | 'frozen'
      ip: ip ? ip.substring(0, 20) : null
    });
  },

  // New account registered
  register(data) {
    const { user_code, account_number, branch, account_type } = data;
    writeEvent('register', user_code, 'user', {
      user_code, account_number, branch, account_type
    });
  },

  // Friend/connection request
  friendRequest(data) {
    const { from_code, to_code, status } = data;
    writeEvent('friend_request', from_code, 'user', {
      from_code, to_code, status // 'sent' | 'accepted' | 'rejected'
    });
  },

  // Account freeze/unfreeze by officer
  accountStatusChange(data) {
    const { user_code, new_status, reason, officer_code } = data;
    const event = new_status === 'frozen' ? 'account_freeze' : 'account_unfreeze';
    writeEvent(event, user_code, 'account', {
      user_code, new_status, reason: reason || null, officer_code
    });
  },

  // Officer action (freeze, file STR, etc.)
  officerAction(data) {
    const { action, target_code, target_id, officer_code, alert_id, notes } = data;
    writeEvent('officer_action', officer_code, 'officer', {
      action, // 'freeze' | 'unfreeze' | 'file_str' | 'close_alert' | 'escalate'
      target_code, target_id,
      officer_code,
      alert_id: alert_id || null,
      notes: notes || null
    });
  },

  // Coupon redeemed
  couponRedeem(data) {
    const { user_code, coupon_code, amount } = data;
    writeEvent('coupon_redeem', user_code, 'user', {
      user_code, coupon_code, amount
    });
  },

  // AI agent analysis completed
  agentAnalysis(data) {
    const { alert_id, entity_code, risk_score, recommendation, patterns, episode_id } = data;
    writeEvent('agent_analysis', entity_code, 'account', {
      alert_id, entity_code,
      risk_score: Math.round(risk_score || 0),
      recommendation,
      patterns: patterns || [],
      episode_id
    });
  },

  // Generic system event
  system(message, data = {}) {
    writeEvent('system', 'server', 'system', { message, ...data });
  }
};

module.exports = logger;
