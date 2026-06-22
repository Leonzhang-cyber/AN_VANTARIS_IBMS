# Module Profile Map v1

## VANTARIS ONE core model

VANTARIS ONE core model defines canonical object meaning, identity semantics, and cross-module interoperability constraints.

## UFMS profile

UFMS profile focuses on fault/event/alarm/evidence workflows and facility operations semantics.

## EDGE/LINK integration runtime profile

EDGE/LINK integration runtime profile focuses on edge acquisition, transport handoff, routing, retry, DLQ, replay, and delivery integration behavior.

## DB profile

DB profile is implementation mapping layer. It persists canonical semantics and operational metadata but does not become contract authority.

## Console profile

Console profile is presentation/API consumer. It must consume contract authority through Code-facing boundaries and should not define private canonical variants.

## NexusAI profile

NexusAI profile is insight/triage consumer. It consumes canonical and event context contracts for recommendation workflows.

## Future product profiles

Future product profiles may include additional building management, maintenance, sustainability, and data-center domains. These profiles remain VANTARIS ONE consumers of `AN_VANTARIS_Contracts` and must not redefine canonical identifiers.

## Cross-profile rule

All profiles consume authority contracts. Runtime sources must not be treated as primary contract definitions.
