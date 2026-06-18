# ONE Adapter A2 Foundation Reference Map

This reference map is docs-level planning only.
It is not a real contract, not a DB schema, not an API, and not a runtime adapter.

## Foundation to Consumer Mapping

| Source reference | Consumer | Purpose | Allowed usage | Forbidden usage | Future promotion requirement |
| --- | --- | --- | --- | --- | --- |
| AN_VANTARIS_Contracts reference | UCore | core operations context linkage | docs-level contract reference interpretation | modify contracts source/schema | separate contract promotion gate |
| AN_VANTARIS_Contracts reference | UMMS | maintenance context linkage | docs-level field mapping references | creating formal contract artifacts in this task | separate contract promotion gate |
| AN_VANTARIS_Contracts reference | UESG | sustainability context linkage | docs-level boundary mapping | direct contracts repository edits | separate contract/schema authorization |
| AN_VANTARIS_Contracts reference | UCDE | evidence semantics linkage | docs-level evidence linkage mapping | direct contract/schema implementation | UCDE formal promotion gate |
| AN_VANTARIS_Contracts reference | UDOC | data operation context linkage | docs-level boundary alignment | schema package creation | separate formal contract gate |
| AN_VANTARIS_Contracts reference | UConsole | status semantics linkage | docs-level status reference mapping | API/schema implementation | UConsole API gate authorization |
| AN_VANTARIS_EDGE reference | UCore | edge context visibility reference | reference-only usage through adapter boundary | direct edge runtime ownership/access | separate runtime authorization |
| AN_VANTARIS_EDGE reference | UMMS | maintenance-event context reference | reference-only mapping | direct edge integration implementation | separate gate authorization |
| AN_VANTARIS_EDGE reference | UESG | energy source context reference | reference-only planning | direct edge runtime implementation | separate gate authorization |
| AN_VANTARIS_EDGE reference | UCDE | evidence source reference | reference-only linkage planning | direct edge ingestion runtime | separate gate authorization |
| AN_VANTARIS_EDGE reference | UDOC | operational telemetry context reference | reference-only planning | direct edge runtime ownership | separate gate authorization |
| AN_VANTARIS_EDGE reference | Reports/Analytics/Nexus AI Consumer | future analytical context reference | future reference planning | direct runtime consumption implementation | future platform module gates |
| AN_VANTARIS_LINK reference | UCore | delivery/status linkage reference | reference-only planning | link runtime ownership | separate gate authorization |
| AN_VANTARIS_LINK reference | UMMS | delivery status context reference | reference-only mapping | direct link integration runtime | separate gate authorization |
| AN_VANTARIS_LINK reference | UESG | sustainability delivery context reference | reference-only planning | direct link runtime implementation | separate gate authorization |
| AN_VANTARIS_LINK reference | UCDE | evidence transport linkage reference | reference-only planning | direct link pipeline implementation | separate gate authorization |
| AN_VANTARIS_LINK reference | UDOC | operations delivery context reference | reference-only planning | direct link runtime ownership | separate gate authorization |
| AN_VANTARIS_DB reference | UCore | metadata context reference | reference-only dependency awareness | DB schema/table ownership | separate DB gate authorization |
| AN_VANTARIS_DB reference | UMMS | maintenance metadata context reference | reference-only planning | table/migration implementation | separate DB gate authorization |
| AN_VANTARIS_DB reference | UESG | sustainability metadata context reference | reference-only planning | direct DB runtime ownership | separate DB gate authorization |
| AN_VANTARIS_DB reference | UCDE | evidence metadata context reference | reference-only planning | DB schema implementation | separate DB gate authorization |
| AN_VANTARIS_DB reference | UDOC | operations metadata context reference | reference-only planning | direct DB runtime access | separate DB gate authorization |
| AN_VANTARIS_DB reference | UConsole/Reports/Analytics | future status/report metadata context | reference-only planning | DB query/runtime implementation | future API/DB gate authorization |
