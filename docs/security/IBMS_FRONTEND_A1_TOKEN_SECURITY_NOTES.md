# IBMS Frontend A1 Token Security Notes

## 1. No hardcoded token

- No sample JWT, API keys, or bearer strings in source
- `TOKEN_STORAGE_KEY` is a storage key name only

## 2. No secret in frontend

- Passwords and signing secrets stay on backend
- Frontend stores access token only after successful login response

## 3. localStorage risk

- Token in `localStorage` is vulnerable to XSS
- Mitigate with CSP, input sanitization, dependency audit
- Document for security review before production

## 4. Future httpOnly cookie option

- If backend supports cookie-based session, migrate token transport
- Would remove localStorage token exposure
- Requires CORS/credentials contract update

## 5. 401 / 403 handling

- **401:** handler should clear local session and navigate to login (A2/A3)
- **403:** handler should navigate to `/403` or show permission message
- Handlers are optional hooks — must be wired explicitly

## 6. menu_api JWT compatibility

- Backend menu routes require JWT (`56234d8`)
- This client attaches Bearer when token exists
- Menu fetch must run after login sets token via `setAccessToken`
- Missing token → 401 from backend — frontend handler should redirect to login

## 7. Non-scope

- No real `.env` created
- No npm install / build
- No backend changes
