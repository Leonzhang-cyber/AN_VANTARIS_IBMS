# AN_VANTARIS_LINK Release Integrity Policy

Status: INSTALL_PACKAGE_FOUNDATION

## Purpose

This policy defines integrity requirements for the LINK independent offline package foundation.

It does not assemble a real production artifact, execute install, start services, approve endpoints,
enable production delivery, connect to UFMS API, access UFMS DB, or enable writeback.

## Required Integrity Inputs

- release manifest
- checksum manifest
- lifecycle manifest
- package manifest
- contracts manifest reference
- package verification script
- local healthcheck script
- rollback / uninstall plan
- typecheck validation
- boundary scan validation

## Integrity Rules

- release manifest must list required package files
- all listed release files must exist
- checksum foundation must exist
- contracts manifest reference must exist
- package verification must pass
- local healthcheck must pass
- typecheck must pass
- boundary scan must pass
- production delivery must remain blocked
- UFMS DB direct access must remain blocked
- writeback must remain blocked

## Runtime Boundary

- realArtifactAssemblyExecuted=false
- realInstallExecuted=false
- serviceStartExecuted=false
- linkRuntimeEnabled=false
- linkProductionDeliveryAllowed=false
- endpointApproved=false
- directUfmsDbAccessAllowed=false
- writebackAllowed=false
- realUfmsApiDeliveryEnabled=false
