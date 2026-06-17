# VANTARIS IBMS Security A4 MQTT Externalization

**Task ID:** IBMS-SECURITY-A4  
**Date:** 2026-06-16  
**Baseline Commit:** `05cc2d0` (A3)

---

## 1. Task Scope

| Item | Status |
|---|---|
| Scope | Externalize MQTT broker config only |
| Device logic changed | ❌ No |
| Topic/payload changed | ❌ No |
| Real MQTT credential committed | ❌ No |
| Service started | ❌ No |

---

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/common/config/default.py` | `MQTT_BROKER_HOST/PORT/USERNAME/PASSWORD` from env |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/hvac_mqtt_simulator.py` | Env-first MQTT constants; dev placeholders |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/air_quality_simulator.py` | Env-first MQTT constants; dev placeholders |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/test_air_quality_receiver.py` | Env-first MQTT constants; dev placeholders |
| `AN_VANTARIS_IBMS-backend/.env.example` | SECURITY-A4 comment |
| `docs/security/IBMS_SECURITY_A4_MQTT_EXTERNALIZATION.md` | This document |

**Unchanged:** `mqtt_driver.py` — broker/credentials still come from per-device config at connect time.

---

## 3. Environment Variables Used

| Variable | Purpose |
|---|---|
| `IBMS_MQTT_HOST` | MQTT broker host |
| `IBMS_MQTT_PORT` | MQTT broker port |
| `IBMS_MQTT_USERNAME` | MQTT username |
| `IBMS_MQTT_PASSWORD` | MQTT password |

---

## 4. Runtime Behavior

- **Environment first:** All listed variables read via `os.getenv` when set.
- **Development fallback:** `127.0.0.1:1883`, `dev-mqtt-user` / `dev-mqtt-password` — not production credentials.
- **No password printing:** Simulators print broker host/port only, not password.
- **Behavior unchanged:** Topics, payloads, publish/subscribe logic untouched.

---

## 5. Not Changed

| Area | Status |
|---|---|
| DB | ❌ Not changed |
| JWT | ❌ Not changed |
| DID | ❌ Not changed |
| Blockchain | ❌ Not changed |
| RBAC | ❌ Not changed |
| Route protection | ❌ Not changed |
| Production simulator disable | ❌ Deferred to SECURITY-A8 |

---

## 6. No Real Secret Confirmation

- Removed hardcoded production broker IP and `hexinic` credentials from testMQTT scripts.
- `.env.example` uses placeholders only.
- No real MQTT password committed in this task.

---

## 7. Recommended Next Tasks

- **IBMS-SECURITY-A5** — DID / blockchain externalization
- **IBMS-SECURITY-A8** — Disable simulators in production
