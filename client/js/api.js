// api.js — Shared utilities: API calls, auth, toast, socket
const API = '/api';

// ─── HTTP HELPERS ─────────────────────────────────────────────────────────────

async function request(method, url, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include'   // send httpOnly cookies
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + url, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

const api = {
  get: (url) => request('GET', url),
  post: (url, body) => request('POST', url, body),
  patch: (url, body) => request('PATCH', url, body),
  del: (url) => request('DELETE', url)
};

// ─── AUTH ─────────────────────────────────────────────────────────────────────

let _currentUser = null;

async function getUser() {
  if (_currentUser) return _currentUser;
  try {
    const { user } = await api.get('/auth/me');
    _currentUser = user;
    return user;
  } catch (e) {
    return null;
  }
}

// Redirect to login if not authenticated. Call at top of every protected page.
async function requireLogin(expectedRole = null) {
  const user = await getUser();
  if (!user) {
    window.location.href = '/client/login.html';
    return null;
  }
  if (expectedRole && user.role !== expectedRole) {
    window.location.href = '/client/login.html';
    return null;
  }
  return user;
}

async function requireOfficerLogin() {
  const user = await getUser();
  if (!user) { window.location.href = '/officer/login.html'; return null; }
  if (user.role !== 'officer') { window.location.href = '/officer/login.html'; return null; }
  return user;
}

async function logout() {
  try { await api.post('/auth/logout'); } catch (e) {}
  _currentUser = null;
  window.location.href = '/client/login.html';
}

async function officerLogout() {
  try { await api.post('/auth/logout'); } catch (e) {}
  _currentUser = null;
  window.location.href = '/officer/login.html';
}

// ─── TOAST NOTIFICATIONS ──────────────────────────────────────────────────────

function ensureToastContainer() {
  let el = document.getElementById('toast-container');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast-container';
    el.className = 'toast-container';
    document.body.appendChild(el);
  }
  return el;
}

function showToast(message, type = 'info', duration = 4000) {
  const container = ensureToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  toast.innerHTML = `
    <span style="font-size:14px;">${icons[type] || 'ℹ'}</span>
    <span style="flex:1;">${message}</span>
    <span class="toast-close" onclick="this.parentElement.remove()">×</span>
  `;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ─── FORMAT HELPERS ──────────────────────────────────────────────────────────

function formatCurrency(amount) {
  return '₹' + parseFloat(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(timestamp) {
  const d = new Date(timestamp * 1000);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) +
    ' ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

function timeAgo(timestamp) {
  const diff = Math.floor(Date.now() / 1000) - timestamp;
  if (diff < 60) return 'just now';
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
  return Math.floor(diff / 86400) + 'd ago';
}

function initials(name) {
  return (name || '?').split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase();
}

// ─── SOCKET.IO ───────────────────────────────────────────────────────────────

let _socket = null;

function initSocket(callbacks = {}) {
  const script = document.createElement('script');
  script.src = '/socket.io/socket.io.js';
  script.onload = () => {
    _socket = io({ withCredentials: true });

    _socket.on('connect', () => console.log('🔌 Socket connected'));
    _socket.on('disconnect', () => console.log('🔌 Socket disconnected'));

    if (callbacks.onTransaction) {
      _socket.on('transaction_received', (data) => {
        showToast(`Received ${formatCurrency(data.amount)} from ${data.from}`, 'success');
        callbacks.onTransaction(data);
      });
    }
    if (callbacks.onFriendRequest) {
      _socket.on('friend_request', (data) => {
        showToast(`Connection request from ${data.from_name}`, 'info');
        callbacks.onFriendRequest(data);
      });
    }
    if (callbacks.onFriendAccepted) {
      _socket.on('friend_accepted', (data) => {
        showToast(`${data.name} accepted your request!`, 'success');
        callbacks.onFriendAccepted(data);
      });
    }
    if (callbacks.onFraudAlert) {
      _socket.on('fraud_alert', callbacks.onFraudAlert);
    }
    if (callbacks.onNewTransaction) {
      _socket.on('new_transaction', callbacks.onNewTransaction);
    }
  };
  document.head.appendChild(script);
  return () => _socket;
}

// ─── FORM HELPERS ─────────────────────────────────────────────────────────────

function setLoading(btn, loading, text = null) {
  if (loading) {
    btn.dataset.originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> ' + (text || 'Loading...');
    btn.disabled = true;
  } else {
    btn.innerHTML = btn.dataset.originalText || 'Submit';
    btn.disabled = false;
  }
}

function showError(elementId, message) {
  const el = document.getElementById(elementId);
  if (el) { el.textContent = message; el.classList.add('visible'); }
}

function clearError(elementId) {
  const el = document.getElementById(elementId);
  if (el) { el.textContent = ''; el.classList.remove('visible'); }
}
