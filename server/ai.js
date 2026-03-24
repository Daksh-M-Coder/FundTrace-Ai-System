const express = require('express');
const router = express.Router();
const logger = require('./logger');

const AGENT_URL = process.env.AGENT_URL || 'http://localhost:5002';

// Proxy to FraudSense agent /health
router.get('/health', async (req, res) => {
  try {
    const resp = await fetch(`${AGENT_URL}/health`, { method: 'GET' });
    const data = await resp.json().catch(() => ({}));
    return res.json({ success: true, agent: data });
  } catch (e) {
    return res.status(502).json({ success: false, error: 'Agent not reachable', detail: e.message });
  }
});

// Proxy to FraudSense agent /analyze
router.post('/analyze', async (req, res) => {
  const payload = {
    task: req.body?.task || 'Analyze fraud risk for this subject',
    entity_code: req.body?.entity_code || null,
    pattern: req.body?.pattern || null,
    alert_id: req.body?.alert_id || null,
    user_id: req.body?.user_id || null,
    backend: req.body?.backend || null,
    model: req.body?.model || null
  };
  try {
    const resp = await fetch(`${AGENT_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json().catch(() => ({}));
    if (!data?.success) {
      return res.status(502).json({ success: false, error: data?.error || 'Agent error' });
    }
    try {
      const ans = data.final_answer || {};
      if (payload.entity_code) {
        logger.agentAnalysis({
          alert_id: payload.alert_id || null,
          entity_code: payload.entity_code,
          risk_score: ans.risk_score,
          recommendation: ans.recommendation,
          patterns: ans.patterns_detected || [],
          episode_id: data.episode_id || null
        });
      }
    } catch (e) {}
    return res.json(data);
  } catch (e) {
    return res.status(502).json({ success: false, error: e.message || 'Agent call failed' });
  }
});

// Proxy to FraudSense agent /chat
router.post('/chat', async (req, res) => {
  const payload = {
    messages: Array.isArray(req.body?.messages) ? req.body.messages : [],
    entity_code: req.body?.entity_code || null,
    pattern: req.body?.pattern || null,
    backend: req.body?.backend || null,
    model: req.body?.model || null
  };
  try {
    const resp = await fetch(`${AGENT_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json().catch(() => ({}));
    return res.status(data?.success ? 200 : 502).json(data);
  } catch (e) {
    return res.status(502).json({ success: false, error: e.message || 'Agent chat failed' });
  }
});

// Proxy to FraudSense agent /forensic — deep account investigation
router.post('/forensic', async (req, res) => {
  const payload = {
    entity_code: req.body?.entity_code || null,
    backend: req.body?.backend || null,
    model: req.body?.model || null
  };
  if (!payload.entity_code) {
    return res.status(400).json({ success: false, error: 'entity_code is required' });
  }
  try {
    const resp = await fetch(`${AGENT_URL}/forensic`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(120000)   // forensic takes longer
    });
    const data = await resp.json().catch(() => ({}));
    return res.status(data?.success ? 200 : 502).json(data);
  } catch (e) {
    return res.status(502).json({ success: false, error: e.message || 'Forensic analysis failed' });
  }
});

module.exports = { router };
