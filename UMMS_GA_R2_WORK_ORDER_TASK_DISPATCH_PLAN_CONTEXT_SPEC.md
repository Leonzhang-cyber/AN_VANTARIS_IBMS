# UMMS GA R2 Work Order Task Dispatch Plan Context Spec

PASS marker: `UMMS_GA_R2_PRODUCTION_GRADE_MAINTENANCE_WORKSPACE_PASS`

UMMS is the Work Management / Maintenance capability for VANTARIS ONE. R2 is production-grade customer demo readiness and remains read-only.

Work order records include:
- `workOrderId`
- `title`
- `description`
- `maintenanceType`
- `assetName`
- `systemName`
- `location`
- `priority`
- `status`
- `assignedRole`
- `assignedEngineer`
- `dueDate`
- `sourceEvent`
- `linkedUhmiPanel`
- `linkedUcdeEvidence`
- `linkedReport`
- `customerVisible`
- `engineerVisible`
- `readOnly`

Maintenance types cover Preventive, Corrective, Inspection, and Customer Acceptance. Status coverage includes Open, In Review, Scheduled, Pending Evidence, and Closed Preview.

Maintenance task records include `taskId`, `taskName`, `workOrderId`, `engineer`, `role`, `status`, `checklistStatus`, `evidenceRequired`, `linkedAsset`, `linkedEvent`, and `readOnly`.

Preventive maintenance plan records include `planId`, `planName`, `systemName`, `assetGroup`, `frequency`, `nextDueDate`, `complianceStatus`, `linkedTasks`, and `readOnly`.

Corrective maintenance flow records include `flowId`, `triggerEvent`, `linkedAsset`, `diagnosticStep`, `workOrderPreview`, `evidenceRequirement`, `approvalBoundary`, and `readOnly`.

Engineer dispatch records include `engineerId`, `engineerName`, `assignedTasks`, `availability`, `siteZone`, `role`, `shift`, and `readOnly`.

R2 does not create work orders, assign tasks, close work orders, approve actions, dispatch engineers, write DB records, control devices, or issue EDGE/LINK commands.
