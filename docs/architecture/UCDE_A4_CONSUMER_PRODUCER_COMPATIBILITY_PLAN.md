# UCDE A4 Consumer Producer Compatibility Plan

UCDE-A4 does not implement producer/consumer integration.
This plan documents future compatibility checks only.

## Future Producers

### UCore
- expected role: provide operation decision and readiness evidence references
- compatibility concern: context-level identity alignment across operations domains
- required future contract check: producer identity and traceability field obligations
- forbidden A4 implementation: no producer integration implementation

### UMMS
- expected role: provide maintenance workflow evidence references
- compatibility concern: work-order lifecycle mapping consistency
- required future contract check: maintenance evidence event normalization
- forbidden A4 implementation: no integration/runtime changes

### UESG
- expected role: provide sustainability/energy evidence references
- compatibility concern: reporting period and context consistency
- required future contract check: sustainability evidence optionality rules
- forbidden A4 implementation: no API/schema implementation

### UDOC
- expected role: provide infrastructure operation evidence references
- compatibility concern: site/rack/room hierarchy mapping consistency
- required future contract check: operations context linkage obligations
- forbidden A4 implementation: no runtime adapter implementation

### UConsole
- expected role: provide status/governance evidence references
- compatibility concern: status semantics alignment with UCDE evidence model
- required future contract check: status evidence contract candidate field alignment
- forbidden A4 implementation: no backend/frontend implementation

### EDGE/LINK delivered references via Shared Foundation
- expected role: provide shared-foundation delivered evidence references
- compatibility concern: ownership and transport boundary clarity
- required future contract check: reference-only ingestion obligations and boundary checks
- forbidden A4 implementation: no direct Edge/Link runtime integration

### UFMS optional evidence reference
- expected role: optional external evidence reference source
- compatibility concern: contamination and ownership confusion risk
- required future contract check: optional-source boundary and classification checks
- forbidden A4 implementation: no UFMS runtime/source import

## Future Consumers

### UCDE
- expected role: consume and organize evidence references
- compatibility concern: cross-source semantics harmonization
- required future contract check: canonical evidence identity and context compatibility
- forbidden A4 implementation: no formal contract runtime usage

### Reports
- expected role: consume approved evidence outputs for reporting
- compatibility concern: report projection stability vs candidate contract changes
- required future contract check: read-model compatibility checklist
- forbidden A4 implementation: no reporting pipeline implementation

### Analytics
- expected role: consume evidence outputs for analysis
- compatibility concern: schema drift impact on analytical models
- required future contract check: analytical compatibility profile
- forbidden A4 implementation: no analytics runtime integration

### Nexus AI shared service
- expected role: consume approved UCDE evidence references
- compatibility concern: safety/classification and provenance requirements
- required future contract check: AI consumer boundary and provenance checks
- forbidden A4 implementation: no AI runtime integration

### UConsole
- expected role: consume governance/status evidence views
- compatibility concern: governance status consistency across modules
- required future contract check: status evidence compatibility checks
- forbidden A4 implementation: no UI/API implementation

### Governance
- expected role: consume readiness/risk/approval evidence summaries
- compatibility concern: decision auditability and rollback traceability
- required future contract check: governance audit field completeness
- forbidden A4 implementation: no governance runtime workflow implementation
