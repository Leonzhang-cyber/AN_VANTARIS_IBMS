# UMMS GA R2 UHMI UCDE Asset Event Report Linkage Spec

PASS marker: `UMMS_GA_R2_PRODUCTION_GRADE_MAINTENANCE_WORKSPACE_PASS`

UMMS R2 links to UHMI / UCDE / Assets / Events / Reports in read-only mode only. The linkage gives the customer product-level continuity without creating runtime authority or write paths.

UHMI Linkage:
- UMMS work orders reference UHMI panels such as System HMI, Device HMI, Alarm & Event HMI, and Evidence & Reports.
- UHMI remains under UConsole / UHMI Workspace.
- UMMS does not execute UHMI commands.

UCDE Evidence Linkage:
- UCDE Evidence Center
- UHMI Evidence Context
- Work Order Evidence
- Task Evidence
- Asset Evidence
- Event Evidence
- Acceptance Evidence
- Validator Evidence
- Release Evidence

Asset context includes `assetId`, `assetName`, `systemName`, `category`, `location`, `zone`, `linkedEvents`, `linkedWorkOrders`, `linkedMaintenancePlans`, `linkedEvidence`, `linkedReports`, and `readOnly`.

Event / Fault Context includes `eventId`, `severity`, `sourceSystem`, `linkedAsset`, `linkedWorkOrder`, `linkedTask`, `evidenceLinked`, `status`, and `readOnly`.

Reports Linkage covers UMMS Maintenance Report, Work Order Summary Report, Engineer Dispatch Report, Customer Acceptance Report, Evidence Trace Report, and Package Readiness Report.

Future controlled action path is recorded and NOT EXECUTED:
`UMMS / UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`
