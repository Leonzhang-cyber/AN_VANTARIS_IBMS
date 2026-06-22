# Industrial Safety and Cyber Boundary v1

## 1. Purpose

Define safety/cyber boundary expectations so cybersecurity controls and industrial safety governance remain aligned.

## 2. Safety function vs monitoring/decision-support function

- Safety function remains OT/system safety-domain responsibility.
- VANTARIS monitoring and decision-support functions provide visibility, diagnostics, and recommendations.

## 3. EDGE/LINK boundary

EDGE/LINK must not bypass OT safety systems.

## 4. UFMS/AI command boundary

UFMS/AI recommendations must not directly actuate safety-critical equipment without approved control workflow.

## 5. Manual approval requirement

Future command features require explicit manual approval and control workflow governance.

## 6. Fail-safe and fail-closed guidance

- Prefer fail-safe defaults for uncertain control states.
- Prefer fail-closed behavior on security validation failures for critical conduits.

## 7. Alarm/event integrity

Alarm/event generation, transport, and replay paths must preserve integrity and traceability.

## 8. Evidence chain

Safety-related and cybersecurity-related actions require auditable evidence references.

## 9. Operational change approval

Security-impacting and safety-impacting operational changes require documented approval and rollback path.

## 10. Customer risk assessment requirement

Customer/site-specific risk assessment is required before enabling any safety-adjacent control workflows.
