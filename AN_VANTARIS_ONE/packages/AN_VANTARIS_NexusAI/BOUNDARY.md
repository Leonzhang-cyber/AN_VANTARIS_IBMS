# AN_VANTARIS_NexusAI Boundary

## Allowed responsibilities

- AI gateway and model interaction
- RCA/RAG workflow orchestration
- inference trace output to CDE pathways

## Forbidden responsibilities

- direct modification of business DB
- uncontrolled self-learning
- bypass of CDE traceability

## Dependencies allowed

- `AN_VANTARIS_Contracts`
- controlled API contracts with `AN_VANTARIS_Code`

## Dependencies forbidden

- direct business DB mutation dependencies
- hidden cross-module private schema contracts
