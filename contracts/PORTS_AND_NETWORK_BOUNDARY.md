# VANTARIS ONE Ports and Network Boundary

## Default Ports

- Edge Local API: 7101
- Link Ingress: 7201
- Link Admin: 7202
- Code API: 7301
- Console Web: 7401
- Console API: 7402
- NexusAI API: 7501
- NexusAI Model API: 7502
- PostgreSQL: 5432
- Metrics: 9100+

## Network Boundary Rules

- Edge must not direct-write DB
- Edge communicates to Link only for delivery in production path
- Link routes to Code/NexusAI/external adapters by policy
- Code accesses DB through approved data access layer
- Console accesses platform through admin APIs
- NexusAI does not mutate business DB directly
- DB has no outbound business calls
- UFMS only through adapter/contract boundary
