# MENU-GA-R1 International GA L1/L2/L3 Menu Architecture Reconciliation

PASS marker: ONE_MENU_GA_R1_INTERNATIONAL_L1_L2_L3_MENU_ARCHITECTURE_PASS

MENU-GA-R1 freezes the VANTARIS ONE / IBMS international GA menu architecture baseline. The model is `L1_L2_LEFT_SIDEBAR_L3_CONTENT_TOP`: L1 and L2 are rendered in the left Sidebar, while L3 is rendered at the top of the content area as page tabs / action row metadata.

## Frozen Rules

- L1 is the left Sidebar domain.
- L2 is the left Sidebar page entry.
- L3 is the content-area page workflow row.
- Sidebar only renders L1 and L2.
- L3 must not be rendered in the Sidebar.
- L3 belongs to the same visual plane as page content.
- The product entry is Dashboard.
- Legacy label Home is not a current menu label.
- Sidebar must support collapse / expand.
- Collapsed Sidebar shows icons and keeps labels available through title / tooltip.
- Sidebar collapse state is stored in localStorage.

## International GA Benchmark

The baseline is benchmarked against Schneider Electric EcoStruxure, Siemens Desigo CC, Honeywell EBI, and Johnson Controls OpenBlue.

## Scenario Coverage

The baseline covers UMMS, UFMS, UESG, Airport, and Data Center scenarios.

## Existing IBMS Mapping

- Server Precheck R1/R2/R3/R4 is mapped under Engineer Workspace > Server Precheck as L3 content navigation.
- Foundation Diagnostics is mapped under Engineer Workspace > Foundation Diagnostics.
- Customer Delivery is mapped under Engineer Workspace > Customer Delivery.
- Local Release Index is mapped under Engineer Workspace > Release Management.
- CODE Policy Gate is mapped under Intelligence > AI Governance, with a secondary mapping under Engineer Workspace > Release Management.
- NexusAI Branch Audit is mapped under Intelligence > NexusAI and Intelligence > AI Governance.
- Reports / Export Center is mapped under Reports & Compliance > Report Center and Export Center.
- Asset Context is mapped under Systems & Assets > Asset Registry and Asset Graph.

## Frontend Baseline

`AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts` carries L1/L2 Sidebar entries and L3 metadata. `AN_VANTARIS_IBMS-frontend/src/components/AppLayout.vue` renders only L1/L2 in the Sidebar and renders the active L2 `l3Items` in the content area top row.

No SSH, deployment, install, DB connection, DB migration, DB write, runtime healthcheck, auth/JWT/RBAC mutation, EDGE/LINK runtime, device control, external API call, or server execution script is part of this task.
