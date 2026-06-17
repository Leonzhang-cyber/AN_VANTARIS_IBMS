# IBMS Frontend A4 API Security Notes

## 1. All API calls go through request.ts

- Domain modules must not import axios directly
- Ensures consistent base URL, headers, and error handling

## 2. Bearer token centralized

- `Authorization: Bearer` added in request interceptor only
- Domain modules assume token already set after login

## 3. No production URL hardcode

- Relative paths only (`/system/permissions`, etc.)
- Base URL from `VITE_IBMS_API_BASE_URL`

## 4. 401 / 403 expected from backend

- Menu, modeling, IoT write, DID mutate routes require JWT
- Permission-enforced routes may return 403 after seed alignment
- UI must handle via A3 error handlers

## 5. Backend remains source of truth

- Frontend API modules are thin clients
- No client-side permission bypass

## 6. System / menu permission pending

- Menu routes: JWT required; fine-grained permission TBD
- System permission CRUD: JWT required
- Document in CONTRACTS-B1 with 403 where `@require_permission` applies

## 7. Non-scope

- No raw API modules copied
- No npm install / build
- No real tokens in source
