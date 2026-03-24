# package.json — Server Scripts and Dependencies

- Name/version: fundtrace-server 1.0.0
- Scripts:
  - `start`: `node index.js`
  - `dev`: `nodemon index.js`
- Dependencies: express, cors, cookie-parser, express-rate-limit, jsonwebtoken, bcrypt, better-sqlite3, socket.io, nanoid/uuid.
- Dev deps: nodemon.

## Impact
- Defines start/dev commands used to run the backend.
- Lists native module `better-sqlite3` which prefers Node LTS on Windows for prebuilt binaries.
