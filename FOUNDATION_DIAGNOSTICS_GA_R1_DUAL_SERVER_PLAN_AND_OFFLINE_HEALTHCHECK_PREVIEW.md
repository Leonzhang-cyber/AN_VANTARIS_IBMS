# Foundation Diagnostics GA R1 Dual Server Plan And Offline Healthcheck Preview

PASS marker: `FOUNDATION_DIAGNOSTICS_GA_R1_ENGINEER_DIAGNOSTICS_WORKSPACE_PASS`

APP / non-DB target: `192.168.60.21`.
Planned components: Frontend, Backend, UConsole, UHMI, UCDE, UMMS, Customer Delivery, Reports, API, and EDGE/LINK engineer diagnostics preview.

DB-only target: `192.168.60.22`.
Planned components: PostgreSQL and DB Foundation.

Healthcheck Preview is read-only and not executed. It does not SSH, does not connect to either server, does not call an external API, and does not access devices.
