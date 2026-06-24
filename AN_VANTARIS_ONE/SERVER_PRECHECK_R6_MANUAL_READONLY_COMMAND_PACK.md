# SERVER-PRECHECK-R6 Manual Read-only Command Pack

PASS marker: ONE_SERVER_PRECHECK_R6_MANUAL_READONLY_OBSERVATION_SCRIPT_PACK_PASS

## Status

This is a manual, copy-reviewed, read-only observation command pack only.

It is not executable. It is not a shell script. It does not authorize execution. It does not include SSH connection commands.

## Manual Approval Requirement

manualApprovalRequiredBeforeUse: true

No command may be used until a separate approval record explicitly authorizes a future read-only observation window and a human reviewer confirms each template.

## Approved Read-only Templates

The following templates are approved for manual review only:

| Order | Template | Purpose | Placeholder Review |
| --- | --- | --- | --- |
| 1 | `hostname` | Confirm host identity. | none |
| 2 | `whoami` | Confirm current account identity. | none |
| 3 | `date` | Capture timestamp context. | none |
| 4 | `uptime` | Observe uptime. | none |
| 5 | `uname -a` | Observe OS kernel and platform. | none |
| 6 | `cat /etc/os-release` | Observe OS release metadata. | none |
| 7 | `df -h` | Observe filesystem capacity. | none |
| 8 | `free -h` | Observe memory capacity. | none |
| 9 | `ps aux` | Observe process list. | none |
| 10 | `systemctl status <APPROVED_SERVICE> --no-pager` | Observe approved service status. | `<APPROVED_SERVICE>` must be approved before use. |
| 11 | `journalctl -u <APPROVED_LOG_UNIT> --no-pager -n 100` | Observe approved service log tail. | `<APPROVED_LOG_UNIT>` must be approved before use. |
| 12 | `ls -al <APPROVED_PATH>` | Observe approved path metadata. | `<APPROVED_PATH>` must be approved before use. |
| 13 | `find <APPROVED_PATH> -maxdepth 2 -type f` | Observe approved path file list. | `<APPROVED_PATH>` must be approved before use. |
| 14 | `cat <APPROVED_NON_SECRET_FILE>` | Observe approved non-sensitive file. | `<APPROVED_NON_SECRET_FILE>` must be approved before use. |
| 15 | `ss -tulpen` | Observe listening sockets and process associations. | none |

## Non-executable Text Block

The block below is text only for review. It is not a shell block and must not be saved as an executable script.

```text
hostname
whoami
date
uptime
uname -a
cat /etc/os-release
df -h
free -h
ps aux
systemctl status <APPROVED_SERVICE> --no-pager
journalctl -u <APPROVED_LOG_UNIT> --no-pager -n 100
ls -al <APPROVED_PATH>
find <APPROVED_PATH> -maxdepth 2 -type f
cat <APPROVED_NON_SECRET_FILE>
ss -tulpen
```

## Review Stop Conditions

- Stop if the reviewed host identity does not match the approved target.
- Stop if any template would need elevated privilege.
- Stop if a placeholder is not explicitly approved.
- Stop if output may expose sensitive material.
- Stop if any write, restart, stop, start, install, upload, or remote-copy action is requested.
- Stop if the observation cannot be completed with this read-only pack.

## Explicit Non-authorization

This command pack does not authorize execution. A separate future approval is required before any manual read-only observation can occur.
