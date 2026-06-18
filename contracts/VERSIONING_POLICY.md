# VANTARIS ONE Contracts Versioning Policy

- platform version and contract version are separate
- package versions are separate

SemVer style:

- MAJOR: breaking change
- MINOR: backward-compatible addition
- PATCH: correction/clarification
- transition suffix allowed before GA

Additional rules:

- public API breaking change requires new major or new namespace
- event schema breaking change requires new schema version
- DB schema change requires migration version
- module/patch/license manifests require their own version
- generated artifacts must include source contract version
