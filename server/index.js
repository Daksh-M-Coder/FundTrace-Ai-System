// index.js — Main server entry point
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const path = require('path');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');

const { seedOfficer } = require('./db');
const { router: authRouter } = require('./auth');
const txnRouter = require('./transactions');
const socialRouter = require('./social');
const { router: fraudRouter } = require('./fraud');
const { router: couponRouter } = require('./coupons');
const { router: aiRouter } = require('./ai');

const app = express();
const server = http.createServer(app);

const JWT_SECRET = process.env.JWT_SECRET || 'fundtrace_jwt_secret_change_in_production_2024';
const PORT = process.env.PORT || 3000;

// ─── SOCKET.IO SETUP ─────────────────────────────────────────────────────────
const io = new Server(server, {
  cors: { origin: '*', methods: ['GET', 'POST'] }
});

// Attach io to app so routes can use it
app.set('io', io);

// Attach io to fraud module for real-time alerts
const fraudModule = require('./fraud');
fraudModule._io = io;

io.on('connection', (socket) => {
  const cookie = socket.handshake.headers.cookie;
  let userId = null;
  let userRole = null;

  // Parse JWT from cookie
  if (cookie) {
    const match = cookie.match(/ft_token=([^;]+)/);
    if (match) {
      try {
        const payload = jwt.verify(match[1], JWT_SECRET);
        userId = payload.userId;
        userRole = payload.role;
      } catch (e) { /* invalid token */ }
    }
  }

  if (userId) {
    // Join personal room
    socket.join(`user_${userId}`);
    console.log(`🔌 User ${userId} connected (${socket.id})`);

    // Officers join the officers room for live alert feed
    if (userRole === 'officer') {
      socket.join('officers');
      console.log(`👮 Officer joined officers room`);
    }
  } else {
    // Allow anonymous connections (they won't get user events)
    console.log(`🔌 Anonymous socket connected (${socket.id})`);
  }

  socket.on('disconnect', () => {
    console.log(`🔌 Socket disconnected (${socket.id})`);
  });

  // Officer: join officer room after auth (if cookie wasn't available at connect time)
  socket.on('join_officers', (data) => {
    if (data?.token) {
      try {
        const payload = jwt.verify(data.token, JWT_SECRET);
        if (payload.role === 'officer') {
          socket.join('officers');
        }
      } catch (e) {}
    }
  });
});

// ─── MIDDLEWARE ──────────────────────────────────────────────────────────────

app.use(cors({
  origin: ['http://localhost:3000', 'http://127.0.0.1:3000'],
  credentials: true
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// General rate limiter — 200 req/15min per IP
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 200,
  message: { error: 'Too many requests. Please slow down.' }
});

// Strict limiter for auth routes — 20 req/15min
// const authLimiter = rateLimit({
//   windowMs: 15 * 60 * 1000,
//   max: 20,
//   message: { error: 'Too many authentication attempts. Please wait 15 minutes.' }
// });

// TEMP: reduce auth limiter window to 5s for local testing
const authLimiter = rateLimit({
  windowMs: 5 * 1000,
  max: 20,
  message: { error: 'Too many authentication attempts. Please wait a moment.' }
});

// Apply general limiter only to API routes (avoid rate-limiting static assets)
app.use('/api', generalLimiter);

// ─── STATIC FILES ────────────────────────────────────────────────────────────

// Serve client app at /
app.use('/client', express.static(path.join(__dirname, '..', 'client')));

// Serve officer app at /officer
app.use('/officer', express.static(path.join(__dirname, '..', 'officer')));

// Root redirect
app.get('/', (req, res) => {
  res.redirect('/client/login.html');
});

// Redirect base paths to login pages
app.get('/client', (req, res) => {
  res.redirect('/client/login.html');
});
app.get('/officer', (req, res) => {
  res.redirect('/officer/login.html');
});

// ─── API ROUTES ──────────────────────────────────────────────────────────────

app.use('/api/auth', authLimiter, authRouter);
app.use('/api/transactions', txnRouter);
app.use('/api/social', socialRouter);
app.use('/api/fraud', fraudRouter);
app.use('/api/coupons', couponRouter);
app.use('/api/ai', aiRouter);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: Date.now(), version: '1.0.0' });
});

// ─── ERROR HANDLER ────────────────────────────────────────────────────────────

app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// ─── START ────────────────────────────────────────────────────────────────────

async function start() {
  await seedOfficer();
  server.listen(PORT, () => {
    console.log('');
    console.log('╔════════════════════════════════════════════╗');
    console.log('║        FundTrace AI — Server Running       ║');
    console.log('╠════════════════════════════════════════════╣');
    console.log(`║  Client App : http://localhost:${PORT}/client  ║`);
    console.log(`║  Officer App: http://localhost:${PORT}/officer ║`);
    console.log(`║  API        : http://localhost:${PORT}/api     ║`);
    console.log('╚════════════════════════════════════════════╝');
    console.log('');
    console.log('  Officer login: officer@fundtrace.bank / Officer@123');
    console.log('');
  });
}

start().catch(console.error);
