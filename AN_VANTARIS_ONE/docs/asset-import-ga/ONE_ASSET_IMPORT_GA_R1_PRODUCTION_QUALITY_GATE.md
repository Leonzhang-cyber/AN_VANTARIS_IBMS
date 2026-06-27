# VANTARIS ONE Asset Import GA R1
## Production Asset Import Quality Gate

## 1. Purpose

This document defines the production-grade asset data import standard for VANTARIS ONE.

Customer-provided asset Excel files must not be imported directly into the Asset Registry. Every import must pass through a controlled quality gate, issue classification, customer review, and final confirmation workflow.

This applies to airport asset databases such as:

- Asset Database Zonewise_Basement_SH_030626.xlsx
- Asset Database Zonewise_Ground Floor_SH_220626.xlsx

## 2. Product Principle

Asset import is a production operation, not a POC shortcut.

The system must:

1. Parse uploaded files.
2. Validate schema.
3. Analyse data quality.
4. Detect duplicates and missing fields.
5. Match assets to zone, floor, location and system domain.
6. Generate a data quality report.
7. Alert the customer before import.
8. Require second confirmation.
9. Record import audit evidence.
10. Support future rollback reference.

## 3. Import Workflow

Upload Asset File  
→ Parse Workbook  
→ Sheet Detection  
→ Schema Validation  
→ Data Quality Analysis  
→ Issue Classification  
→ Customer Review  
→ Optional Fix / Mapping  
→ Second Confirmation  
→ Import Commit  
→ Import Audit Record  
→ Import Result Report

## 4. Required Validation Areas

### 4.1 Required Field Validation

The following fields must be checked:

- Device ID
- Building
- Level
- Zone
- System
- Location
- Device Type

Missing values in required fields must be classified as BLOCKER or MAJOR depending on impact.

### 4.2 Uniqueness Validation

The system must check:

- Duplicate Device ID within the same sheet.
- Duplicate Device ID across multiple sheets.
- Duplicate Device ID with conflicting System.
- Duplicate Device ID with conflicting Location.
- Duplicate Device ID with conflicting Device Type.

### 4.3 Standard Dictionary Validation

The system must validate and normalize:

- Level
- Zone
- System
- Device Type
- Location
- DA
- Status

### 4.4 Spatial Matching Validation

The system must check whether asset records can be matched to:

- Terminal
- Floor
- Zone
- DA
- Space / Location
- HMI map layer

Unmatched locations must be reported before import.

### 4.5 Maintenance Data Validation

The system must check:

- Last Done
- Due Date
- Status
- Overdue
- Remarks

Missing maintenance data should not always block import, but must be visible in the quality report.

## 5. Issue Severity

### 5.1 BLOCKER

BLOCKER issues prevent import.

Examples:

- Device ID is missing.
- Device ID is duplicated and cannot be resolved.
- System is missing.
- Device Type is missing.
- Level or Zone is missing.
- Workbook structure does not match supported template.

### 5.2 MAJOR

MAJOR issues allow preview but require review.

Examples:

- Location is missing.
- Location cannot be matched to the HMI map.
- System value is not recognized.
- Device Type is not recognized.
- Same Device ID has conflicting attributes.

### 5.3 WARNING

WARNING issues can be accepted with confirmation.

Examples:

- Last Done is missing.
- Due Date is missing.
- Status is missing.
- Area is empty.
- Remarks are empty.
- Location naming appears inconsistent but has suggested normalization.

### 5.4 INFO

INFO issues are informational only.

Examples:

- New system type detected.
- New device type detected.
- New location detected.
- New DA code detected.

## 6. Quality Report

Every upload must generate a Data Quality Report.

The report must include:

- Import batch ID
- Source file name
- Uploaded by
- Upload timestamp
- Total records
- Sheet count
- Zone count
- System count
- Device type count
- Duplicate Device ID count
- Missing required field count
- Unmatched location count
- Warning count
- Import readiness status
- Recommended actions

## 7. UI Alert Requirement

After upload, the system must show an import quality alert.

The alert must show:

- File name
- Total records
- Systems detected
- Zones detected
- Critical issues
- Major issues
- Warnings
- Import readiness

If BLOCKER issues exist:

- Confirm Import button must be disabled.
- User must review and fix issues first.

If only WARNING issues exist:

- Confirm Import button can be enabled.
- User must provide second confirmation.

## 8. Second Confirmation Requirement

Before committing import, the system must show a second confirmation modal.

The modal must include:

- New asset count
- Updated asset count
- Skipped record count
- Accepted warning count
- Import scope
- Acknowledgement checkboxes

Required acknowledgements:

- I have reviewed the Data Quality Report.
- I understand unresolved warnings will be recorded in the import audit log.

Only after acknowledgement can the user click Confirm and Import.

## 9. Import Audit

Each import must generate an audit record.

Audit fields:

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

## 10. Menu Placement

No menu changes are required.

Primary placement:

Assets & Locations  
→ Asset Registry

Related L3 areas:

- Asset Lifecycle Evidence
- Asset Ownership Audit
- Zone-to-Asset Mapping
- System-to-Asset Map
- Point / Tag Overlay
- Point Mapping Evidence
- Tag Readiness Gate

## 11. Production Acceptance Criteria

The import function is GA-ready only when:

1. Asset Excel upload does not directly write to registry.
2. Data quality report is generated before import.
3. BLOCKER / MAJOR / WARNING / INFO issue levels are supported.
4. Customer sees alert before import.
5. Import is blocked when BLOCKER issues exist.
6. Second confirmation is required before commit.
7. Import audit record is created.
8. Imported assets are traceable to source file and import batch.
9. Menu freeze remains intact.
10. No backend, API, router or menu changes are made unless separately approved.

