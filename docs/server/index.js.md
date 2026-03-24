# index.js — Server Bootstrap and Routing

- Purpose: Creates Express app + HTTP server, attaches Socket.IO, applies middlewares, serves static clients, and mounts APIs.
- Key libs: express, http, socket.io, cookie-parser, cors, express-rate-limit, jsonwebtoken.

## Rate Limiting (15-minute windows)
- General limiter: 200 requests per IP per 15 minutes.
- Auth limiter: 20 requests per 15 minutes specifically on `/api/auth/*`.
- Effect: Frequent login attempts (even successful) will eventually hit 429 if exceeding 20 in 15 minutes.
- Location in code: limiter definitions ~97–108; applied to auth routes ~127.

## Static and Routes
- Static: `/client` → client UI; `/officer` → officer portal.
- Root `/` redirects to `/client/login.html`.
- APIs: `/api/auth`, `/api/transactions`, `/api/social`, `/api/fraud`.
- Health check: `/api/health`.

## Socket.IO
- Attaches io to app and to `fraud` module (`fraudModule._io = io`) for realtime alerts.
- Per-connection:
  - Parses `ft_token` cookie and joins `user_{id}` room.
  - Officers join `officers` room for live fraud and transaction feed.

## Startup
- Calls `seedOfficer()` to ensure a default officer account exists.
- Logs URLs and officer credentials on start.
