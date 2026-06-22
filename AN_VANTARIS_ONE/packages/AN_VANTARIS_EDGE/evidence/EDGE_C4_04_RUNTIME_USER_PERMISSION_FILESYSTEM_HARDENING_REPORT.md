# EDGE C4-04 Runtime User / Permission / Filesystem Hardening Report

## Scope

This report captures `UFMS-EDGE-C4-04` foundation-only runtime hardening scaffolding under `AN_VANTARIS_EDGE/**`.

## Baseline commit

- `6b76fa9 feat(edge): add sbom dependency inventory foundation`

## Foundation classification

- `HARDENING_FOUNDATION_ONLY`

## Runtime user/group target

- Runtime user target: `vantaris-edge`
- Runtime group target: `vantaris-edge`
- Dedicated identity required in production model.

## Root execution prohibition

- `rootExecutionAllowed=false`
- Interactive login is disabled in policy model.

## Filesystem ownership model

- Machine-readable ownership model is defined for release, shared, runtime, lifecycle, pointer, and sensitive paths.
- Ownership and mode plan is declarative only in C4-04.

## Permission matrix

- Directory and file mode recommendations are defined.
- Forbidden mode set includes `0777` and `0666`.
- Forbidden flag set includes `setuid` and `setgid`.

## Immutable release policy

- Release tree is immutable to runtime.
- Runtime write access to release tree is prohibited.

## Writable shared paths

- Runtime writable scope is bounded to shared operational directories only.
- Lifecycle and backup paths remain deployment-controlled.

## Sensitive file policy

- Secret and certificate private material policy entries are non-plaintext and non-repository-tracked.
- Real secret material remains absent in C4-04.

## Umask policy

- Runtime umask recommendation: `0027`
- Deployment umask recommendation: `0027`
- Secret provisioning umask recommendation: `0077`

## Symlink policy

- Pointer symlink model (`current`, `previous`) is sandbox-only in C4-04.
- Symlink escape outside sandbox/base path is rejected.

## Executable policy

- Executable inventory is restricted to deployment and validation shell scripts.
- Non-script artifacts are not permitted to be executable.

## Systemd recommendations

- Hardening recommendations recorded as not applied (`appliedByC4_04=false`).
- Includes `User`, `Group`, `NoNewPrivileges`, `ProtectSystem`, `ProtectHome`, `ReadWritePaths`, `ReadOnlyPaths`, and `UMask` guidance.

## Sandbox simulation

- All path, permission, pointer, and symlink safety checks are executed in `.runtime/c4-04-sandbox`.
- No real host permissions or ownership are modified.

## Dry-run result

- `edge-c4-runtime-hardening-dry-run: PASS`

## Lightweight smoke result

- `edge-c4-runtime-hardening-smoke: PASS`

## Production limitations

- C4-04 does not create real users/groups.
- C4-04 does not apply real chown/chmod.
- C4-04 does not apply systemd changes.
- C4-04 does not modify system paths.

## Explicit safety statements

- Explicit no-user-creation statement: no runtime user/group creation performed.
- Explicit no-real-chown/chmod statement: no real ownership or mode mutation performed.
- Explicit no-systemd-change statement: recommendations only, not applied.
- Explicit no-system-path-write statement: no writes under `/opt`, `/etc`, `/var`, `/usr`.
- Explicit no-network statement: no network actions performed.

## Acceptance result

`HARDENING_FOUNDATION_ACCEPTED_NOT_APPLIED`

## Readiness key

`UFMS_EDGE_C4_04_RUNTIME_USER_PERMISSION_FILESYSTEM_HARDENING_PASS`
