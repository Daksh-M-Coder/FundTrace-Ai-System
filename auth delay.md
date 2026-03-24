**Where To Change**
- Brute‑force window in auth.js
  - Location: [auth.js:95–103](file:///c:/Users/daksh/Programmer/Learning/COMP%20TECH%20SKILL/LOW%20CODE%20PROJECTS/FundTrace%20AI%20system/server/auth.js#L95-L103)
  - Original line:
    - const windowStart = Math.floor(Date.now() / 1000) - 15 * 60;
  - Paste this right above with your change so it’s easy to revert:

    ```js
    // TEMP: 5-second brute-force window for testing
    const windowStart = Math.floor(Date.now() / 1000) - 5;
    ```

- Auth route rate limiter in index.js
  - Location: [index.js:103–108](file:///c:/Users/daksh/Programmer/Learning/COMP%20TECH%20SKILL/LOW%20CODE%20PROJECTS/FundTrace%20AI%20system/server/index.js#L103-L108)
  - Original block:
    - const authLimiter = rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 20,
      message: { error: 'Too many authentication attempts. Please wait 15 minutes.' }
    });
  - Paste this block (comment + change) to reduce window to 5 seconds for testing:

    ```js
    // TEMP: reduce auth limiter window to 5s for local testing
    const authLimiter = rateLimit({
      windowMs: 5 * 1000,
      max: 20,
      message: { error: 'Too many authentication attempts. Please wait a moment.' }
    });
    ```

**Why Both**
- The brute‑force block (auth.js) looks at failed attempts in the last 15 minutes; changing to 5 seconds prevents long lockouts.
- The auth limiter (index.js) caps all auth requests over 15 minutes; frequent register/login calls will hit this even if successful. Changing to 5 seconds lets you re‑try quickly.

**After Editing**
- Restart the server from the server directory:
  - npm start
- When you’re done testing, revert the two “TEMP” changes back to 15 minutes:
  - auth.js: 15 * 60
  - index.js: 15 * 60 * 1000

