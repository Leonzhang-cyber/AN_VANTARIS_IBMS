# Reports GA R13 Export Center Preview Spec

PASS marker: `REPORTS_GA_R13_CUSTOMER_DEMO_REPORT_PACK_EXPORT_CENTER_PASS`

Export Center Preview supports PDF Preview, Excel Preview, CSV Preview, and Evidence Bundle Preview. It only shows export queue and format readiness.

No Real Export Execution. No PDF Generation. No Excel Generation. No ZIP Generation. No DB Write. No Evidence Write. No Runtime Activation. No Production Activation.

Future real export must go through `CODE -> Policy Gate -> Approval -> Audit/UCDE -> Export Artifact`.
