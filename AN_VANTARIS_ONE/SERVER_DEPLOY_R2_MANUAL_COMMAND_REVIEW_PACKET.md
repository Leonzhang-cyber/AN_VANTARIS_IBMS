# SERVER-DEPLOY-R2 Manual Command Review Packet

PASS marker: ONE_SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET_PASS

## Manual Review Only

This file records placeholder command templates for human review only. It is not an executable script, not a runbook authorization, and not a production command source.

## Placeholder Rules

- Use `<APP_SERVER>`, `<DB_SERVER>`, `<INSTALL_USER>`, `<PACKAGE_SOURCE>`, `<PACKAGE_MANAGER>`, `<RUNTIME_PACKAGE_NAME>`, `<PROCESS_MANAGER>`, `<SERVICE_NAME>`, and `<DB_TOOL>` placeholders.
- Do not include real hostnames, IP addresses, usernames, domains, passwords, private keys, customer server names, or production credentials.
- Do not copy these templates into a server session without a later approved execution stage.

## APP Runtime Review Templates

- Package manager review template: `<PACKAGE_MANAGER> install <RUNTIME_PACKAGE_NAME>`.
- Process manager review template: `<PROCESS_MANAGER> status <SERVICE_NAME>`.
- Runtime presence review template: `<RUNTIME_TOOL> --version`.
- Service status review template: `<SERVICE_MANAGER> status <SERVICE_NAME>`.

These are templates only. R2 does not install Python, Node.js, PM2, or Nginx.

## DB Runtime Review Templates

- DB tool version review template: `<DB_TOOL> --version`.
- Backup tooling review template: `<BACKUP_TOOL> --version`.
- Restore tooling review template: `<RESTORE_TOOL> --version`.

These are templates only. R2 does not install PostgreSQL, run psql, create DB users, grant privileges, migrate, back up, restore, or seed.

## Evidence Template

Future execution evidence must be redacted and must use restricted raw evidence references when raw command output contains hostnames, IPs, usernames, emails, customer server names, secrets, or production paths.

## Boundary Confirmation

- No SSH execution.
- No APP/DB server connection.
- No runtime installation.
- No command execution by this packet.
- No production target stored in public packet.

## PASS Marker

ONE_SERVER_DEPLOY_R2_RUNTIME_INSTALLATION_EXECUTION_PACKET_PASS
