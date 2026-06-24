# SERVER-PRECHECK-R4 Read-only SSH Execution Approval Packet

PASS marker: ONE_SERVER_PRECHECK_R4_READONLY_SSH_EXECUTION_APPROVAL_PACKET_PASS

## Purpose

SERVER-PRECHECK-R4 creates the read-only SSH execution approval packet for VANTARIS ONE. It is an approval artifact only. It does not execute SSH, generate an executable SSH script, collect credentials, deploy, install, connect to databases, mutate runtime state, or perform any system action.

## Relation to R1/R2/R3

- SERVER-PRECHECK-R1 records the dual-server read-only environment audit baseline.
- SERVER-PRECHECK-R2 records the approved read-only access window plan.
- SERVER-PRECHECK-R3 records the actual approved read-only observation plan.
- SERVER-PRECHECK-R4 freezes the human approval packet that must be accepted before any future read-only SSH observation.

## Approval Packet Lifecycle

1. Prepare the approval packet.
2. Review the read-only command whitelist.
3. Review the forbidden command blacklist.
4. Confirm stop conditions.
5. Confirm evidence capture and redaction rules.
6. Capture human approval outside this repository.
7. Proceed to a future observation only after explicit approval.

## Human Approval Gates

- Customer approval is required before any SSH access.
- Security approval is required before any SSH access.
- Operator or engineer acknowledgement is required before command copy.
- Approval must identify the approved servers, approved window, approved account, approved commands, and evidence owner.
- Approval does not permit deployment, install, DB mutation, auth mutation, secrets handling, or runtime action.

## Read-only Command Whitelist

The following command patterns are allowed only after human approval and only for read-only observation:

- `hostname`
- `whoami`
- `date`
- `uptime`
- `uname -a`
- `df -h`
- `free -h`
- `ps aux`
- `systemctl status <approved-service>`
- `journalctl -u <approved-service> --no-pager -n 100`
- `ls -al <approved-path>`
- `cat <approved-non-secret-file>`
- `find <approved-path> -maxdepth 2 -type f`

## Forbidden Command Blacklist

The following command patterns are forbidden:

- `sudo`
- `su`
- `chmod`
- `chown`
- `rm`
- `mv`
- `cp`
- `mkdir`
- `touch`
- `vi`
- `vim`
- `nano`
- `systemctl restart`
- `systemctl stop`
- `systemctl start`
- `systemctl enable`
- `systemctl disable`
- `service restart`
- `kill`
- `pkill`
- `docker`
- `docker compose`
- `kubectl`
- `npm install`
- `pip install`
- `apt`
- `yum`
- `dnf`
- `systemctl edit`
- `crontab`
- `psql write operations`
- `mysql write operations`
- any command containing password, token, secret, or private key output

## Stop Conditions

- Stop if the server identity does not match the approved target.
- Stop if elevated privilege is requested.
- Stop if a command is not on the whitelist.
- Stop if output may expose sensitive material.
- Stop if customer or security owner withdraws approval.
- Stop if runtime mutation appears necessary.
- Stop if DB mutation appears necessary.
- Stop if evidence capture fails.

## Evidence Capture Rules

- Capture the approval record.
- Capture the command whitelist version.
- Capture the forbidden command blacklist version.
- Capture terminal transcript only during a future approved observation.
- Capture output files with timestamps and server identity.
- Capture stop-condition events.
- Capture final observation decision.

## Redaction Rules

- Redact passwords, tokens, private keys, certificates, credential strings, and secret-like values.
- Do not paste secrets into this repository.
- Do not store credential material in registry files, Markdown, screenshots, transcripts, or logs.
- Stop capture and escalate if sensitive material appears.

## Rollback / No-op Statement

R4 is a no-op approval packet. There is no runtime state to roll back because no SSH execution, deployment, install, DB migration, DB write, auth mutation, EDGE/LINK action, or device control is performed.

## Security Boundary

- sshExecutionAllowed: false.
- deploymentAllowed: false.
- installAllowed: false.
- dbMutationAllowed: false.
- authMutationAllowed: false.
- secretsMutationAllowed: false.
- runtimeActionAllowed: false.
- approvalRequiredBeforeAnySsh: true.
- humanApprovalRequired: true.

## Final Pass Marker

ONE_SERVER_PRECHECK_R4_READONLY_SSH_EXECUTION_APPROVAL_PACKET_PASS
