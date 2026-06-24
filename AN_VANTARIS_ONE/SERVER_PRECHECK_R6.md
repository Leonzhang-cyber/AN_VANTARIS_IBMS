# SERVER-PRECHECK-R6 Manual Read-only Observation Script Pack

PASS marker: ONE_SERVER_PRECHECK_R6_MANUAL_READONLY_OBSERVATION_SCRIPT_PACK_PASS

## Purpose

SERVER-PRECHECK-R6 defines a manual, copy-reviewed, read-only observation command pack for a possible future approved observation. It is documentation and registry only.

R6 is not executable and does not authorize execution. It does not create SSH connection commands, executable shell scripts, frontend routes, backend APIs, deployment actions, install actions, database actions, authentication changes, runtime actions, or secrets handling.

## Relationship to Prior Gates

- R4 source marker: ONE_SERVER_PRECHECK_R4_READONLY_SSH_EXECUTION_APPROVAL_PACKET_PASS
- R4F source marker: ONE_SERVER_PRECHECK_R4F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS
- R5 source marker: ONE_SERVER_PRECHECK_R5_ACTUAL_READONLY_OBSERVATION_ENTRY_GATE_PASS
- R5F source marker: ONE_SERVER_PRECHECK_R5F_FINAL_VERIFICATION_AND_RELEASE_INDEX_UPDATE_PASS

R6 depends on the R4 approval packet and R5 entry gate, but it remains a manual command template pack only.

## Boundaries

- sshExecutionAllowed: false
- sshConnectionCommandsIncluded: false
- executableShellScriptCreated: false
- frontendCreated: false
- backendCreated: false
- routesCreated: false
- deploymentAllowed: false
- installAllowed: false
- dbMutationAllowed: false
- authMutationAllowed: false
- runtimeActionAllowed: false
- secretsHandlingAllowed: false
- menuGaR1R2MutationAllowed: false
- serverPrecheckR4R5MutationAllowed: false
- manualApprovalRequiredBeforeUse: true

## Command Pack

The command templates are maintained in:

`AN_VANTARIS_ONE/SERVER_PRECHECK_R6_MANUAL_READONLY_COMMAND_PACK.md`

The pack is Markdown only. It is not a shell script, not executable automation, and not an authorization to access any server.

## Human Review Rules

1. A human must review every command before use.
2. Approved placeholders must be replaced manually outside this repository.
3. Any command not listed in the pack is out of scope.
4. Any sensitive output must stop the observation and trigger redaction/escalation.
5. Any request for elevated privilege, write action, restart, stop, start, install, upload, or remote copy is out of scope.

## Final PASS Marker

ONE_SERVER_PRECHECK_R6_MANUAL_READONLY_OBSERVATION_SCRIPT_PACK_PASS
