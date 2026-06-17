# VANTARIS IBMS Frontend

This is the sanitized target frontend package for VANTARIS IBMS.

Current stage: SPLIT-B3 target skeleton only.

Rules:
- Do not copy the raw frontend wholesale.
- Do not commit secrets.
- Do not commit node_modules, dist, cache, or raw large assets without review.
- API base URL must be environment-driven.
- Bearer token handling must be centralized.
- 401/403 handling must be standardized.

Source reference:
- Raw source: ../AN_VANTARIS_IBMS-ibms_front/ (read-only, ignored)
- Main placeholder: ../AN_VANTARIS_IBMS-main/
