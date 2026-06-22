# AN_VANTARIS_LINK Rollback and Uninstall Plan

Status: STRUCTURE_ONLY

## Purpose

This document defines the offline rollback and uninstall plan for AN_VANTARIS_LINK.

It does not execute rollback, uninstall, service start, production delivery, endpoint approval,
UFMS API delivery, direct UFMS DB access, or writeback.

## Rollback Scope

Rollback may cover:

- package directory replacement
- config reference restoration
- service template restoration
- manifest restoration
- local healthcheck re-run
- local verification re-run

Rollback must not:

- delete operational evidence
- delete audit evidence
- delete diagnostics evidence
- modify UFMS backend/frontend
- modify DB/schema/migration
- modify auth/login/credentials
- enable production delivery
- approve endpoints
- enable writeback
- enable direct UFMS DB access

## Uninstall Scope

Uninstall may cover future removal of:

- service template
- package files
- local dry-run service registration
- temporary package staging files

Uninstall must not:

- remove retained evidence without explicit approval
- remove audit chain evidence
- remove diagnostics bundles
- remove contracts references
- remove UFMS data
- remove EDGE data
- remove credentials
- modify production systems

## Required Checks Before Rollback

Before rollback:

- package manifest must exist
- verification script must pass
- local healthcheck must pass or produce diagnostic failure
- current package version must be recorded
- target rollback version must be recorded
- production delivery must remain blocked

## Required Checks After Rollback

After rollback:

- verify-link-offline-package.sh must pass
- healthcheck-link-offline.sh must pass
- link-boundary-scan must pass
- typecheck must pass
- production delivery must remain blocked

## Required Checks Before Uninstall

Before uninstall:

- operator approval must be documented
- evidence retention decision must be documented
- package state must be recorded
- production delivery must remain blocked

## Boundary

- linkProductionDeliveryAllowed=false
- endpointApproved=false
- directUfmsDbAccessAllowed=false
- writebackAllowed=false
- consumerImplementationIncluded=false
- realUfmsApiDeliveryEnabled=false
