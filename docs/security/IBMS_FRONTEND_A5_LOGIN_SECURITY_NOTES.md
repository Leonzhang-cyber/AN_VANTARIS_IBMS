# IBMS Frontend A5 Login Security Notes

## 1. No hardcoded credentials

- Login form has no default DID, challenge, signature, or password values
- User must enter credentials at runtime

## 2. No token logging

- Errors show generic messages only
- Full API response bodies are not printed to console in LoginView

## 3. localStorage risk

- Token stored via `setAccessToken` (localStorage)
- XSS could exfiltrate token — mitigate with CSP and dependency audit

## 4. Backend remains source of truth

- Signature/challenge validation happens on server
- Frontend does not verify JWT locally beyond presence check

## 5. 401 clears local session

- Request interceptor + A3 handlers clear session on unauthorized API calls
- Login failures show inline error without persisting partial state

## 6. Future httpOnly cookie option

- If backend adds cookie-based auth, remove localStorage token storage
- Requires CORS/credentials contract update

## 7. Raw login not copied

- Raw `Login.vue` may contain production URL patterns and demo data — not migrated
- New minimal form aligned to backend DID challenge contract only

## 8. Non-scope

- No npm install / build / dev
- No real `.env` or secrets in source
