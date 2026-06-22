# AN_VANTARIS_LINK Release Layout
Status: INSTALL_PACKAGE_FOUNDATION
## Purpose
This document defines the independent LINK offline release layout.
It does not execute install, start services, approve endpoints, enable production delivery,
connect to UFMS API, access UFMS DB, or enable writeback.
## Package Root
Expected future package root:
/opt/an-vantaris-link
## Config Root
Expected future config root:
/etc/an-vantaris-link
## Data Root
Expected future local data root:
/var/lib/an-vantaris-link
## Log Root
Expected future log root:
/var/log/an-vantaris-link
## Bundle Layout
Required bundle paths:
- deploy/offline-bundle/README.md
- deploy/offline-bundle/config/link.env.example
- deploy/offline-bundle/systemd/an-vantaris-link.service.template
- deploy/offline-bundle/manifests/link-offline-package-manifest.v1.json
- deploy/offline-bundle/lifecycle/LIFECYCLE_MANIFEST.link.json
- deploy/offline-bundle/docs/ROLLBACK_AND_UNINSTALL_PLAN.md
- deploy/offline-bundle/docs/RELEASE_LAYOUT.link.md
- deploy/offline-bundle/scripts/install-link.sh
- deploy/offline-bundle/scripts/uninstall-link.sh
- deploy/offline-bundle/scripts/rollback-link.sh
- deploy/offline-bundle/scripts/verify-link-offline-package.sh
- deploy/offline-bundle/scripts/healthcheck-link-offline.sh
## Runtime Boundary
- realInstallExecuted=false
- serviceStartExecuted=false
- linkRuntimeEnabled=false
- linkProductionDeliveryAllowed=false
- endpointApproved=false
- directUfmsDbAccessAllowed=false
- writebackAllowed=false
- realUfmsApiDeliveryEnabled=false
