# ONE-ASSET-IMPORT-GA-R1
# Production Asset Import Quality Gate

## 1. Task Objective

Build the production-grade design baseline for customer asset Excel import.

This is not a POC data import.  
This is a GA production import quality gate for VANTARIS ONE.

The system must prevent unsafe asset data from being imported directly into the Asset Registry.

## 2. Scope

Customer asset files:

- Asset Database Zonewise_Basement_SH_030626.xlsx
- Asset Database Zonewise_Ground Floor_SH_220626.xlsx

Target product areas:

- Assets & Locations → Asset Registry
- Assets & Locations → Floor Plan / HMI Map
- Assets & Locations → Point & Tag Governance
- Reports & Documents → Export & Evidence Center
- Governance & Security → Audit Trail

No menu change is allowed.

## 3. Required Workflow

Upload Asset File  
→ Parse Workbook  
→ Detect Sheets  
→ Validate Schema  
→ Analyse Data Quality  
→ Classify Issues  
→ Generate Data Quality Report  
→ Show Import Alert  
→ Customer Review  
→ Optional Fix / Mapping  
→ Second Confirmation  
→ Commit Import  
→ Create Import Audit Record

## 4. Required Quality Checks

### Required Fields

- Device ID
- Building
- Level
- Zone
- System
- Location
- Device Type

### Duplicate Checks

- Duplicate Device ID in same sheet
- Duplicate Device ID across sheets
- Duplicate Device ID with conflicting System
- Duplicate Device ID with conflicting Location
- Duplicate Device ID with conflicting Device Type

### Dictionary Checks

- Level normalization
- Zone normalization
- System normalization
- Device Type normalization
- Location normalization
- DA normalization

### Spatial Checks

- Asset can match terminal
- Asset can match floor
- Asset can match zone
- Asset can match location / space
- Asset can be placed on HMI / floor map layer

### Maintenance Checks

- Last Done
- Due Date
- Status
- Overdue
- Remarks

## 5. Issue Severity

### BLOCKER

Import must be blocked.

Examples:

- Missing Device ID
- Duplicate Device ID with unresolved conflict
- Missing System
- Missing Device Type
- Missing Building / Level / Zone
- Unsupported workbook structure

### MAJOR

Import preview is allowed, but customer review is required.

Examples:

- Missing Location
- Location cannot match HMI map
- Unknown System
- Unknown Device Type
- Same Device ID has conflicting attributes

### WARNING

Import can continue only after acknowledgement.

Examples:

- Missing Last Done
- Missing Due Date
- Missing Status
- Empty Area
- Empty Remarks
- Location spelling inconsistency

### INFO

Information only.

Examples:

- New Location detected
- New Device Type detected
- New System detected
- New DA code detected

## 6. Import Alert Requirement

After upload, system must show a modal:

Asset Import Quality Check

Required fields:

- File name
- Total records
- Sheets detected
- Zones detected
- Systems detected
- Device types detected
- BLOCKER count
- MAJOR count
- WARNING count
- INFO count
- Import readiness status

If BLOCKER > 0:

- Confirm Import must be disabled.
- User must review and fix issues.

If BLOCKER = 0 and WARNING > 0:

- Confirm Import is enabled only after second confirmation.

## 7. Second Confirmation Requirement

Before import commit, system must show:

Confirm Asset Import

Required summary:

- New assets
- Updated assets
- Skipped records
- Accepted warnings
- Import batch ID
- Source file name

Required checkboxes:

- I have reviewed the Data Quality Report.
- I understand unresolved warnings will be recorded in the import audit log.

## 8. Import Audit Requirement

Each import must generate:

- import_batch_id
- source_file_name
- source_file_hash
- uploaded_by
- uploaded_at
- validated_at
- confirmed_by
- confirmed_at
- total_records
- created_assets
- updated_assets
- skipped_records
- blocker_count
- major_count
- warning_count
- quality_score
- import_status
- rollback_reference

## 9. Acceptance Criteria

- Menu freeze remains intact.
- static-menu.ts is not changed.
- Asset Excel does not import directly.
- Data Quality Report is generated before import.
- BLOCKER / MAJOR / WARNING / INFO levels are supported.
- Alert modal appears before import.
- BLOCKER disables import confirmation.
- Second confirmation is required before commit.
- Import audit record is created.
- Imported assets remain traceable to source file and import batch.
