# VANTARIS ONE Versioning

## 1. Platform Version

Initial target platform version:

VANTARIS ONE Platform: 0.1.0-transition

Notes:

- Not a GA version.
- Not a runtime-ready version.
- Represents transition skeleton and governance baseline only.

## 2. Package Version Policy

Independent package versions:

- AN_VANTARIS_EDGE: 0.0.0-skeleton
- AN_VANTARIS_LINK: 0.0.0-skeleton
- AN_VANTARIS_Code: 0.0.0-skeleton
- AN_VANTARIS_Console: 0.0.0-skeleton
- AN_VANTARIS_NexusAI: 0.0.0-skeleton
- AN_VANTARIS_DB: 0.0.0-skeleton
- AN_VANTARIS_Contracts: 0.0.0-skeleton / current contracts PARTIAL

## 3. Versioning Rules

- platform version and package versions are separate
- runtime package version cannot be raised without source migration
- Contracts version must advance before breaking API/schema changes
- DB schema version must be controlled by AN_VANTARIS_DB
- module version must be tied to module manifest later
- patch version must be tied to patch manifest later
- license feature version must be tied to license contract later
