# VANTARIS ONE Deployment Model

## Mode A — All-in-One Lab / Small Site

- Edge / Link / Code / Console / DB / NexusAI 可在一台服务器
- 仅用于实验室、小项目、开发环境
- 不作为大型生产推荐

## Mode B — Standard Production

- Edge Gateway 单独部署
- Link Server 单独部署
- Code + Console 单独部署
- DB 单独部署
- NexusAI 可选独立部署

## Mode C — High Availability Production

- 多 Edge
- Link active-standby or cluster
- Code multi-node
- DB primary/standby
- Console HA optional
- NexusAI independent pool

## Mode D — High Security / OT Segmented

- Edge in OT zone
- Link as conduit
- Code in application zone
- DB in data zone
- Console in management zone
- optional data-diode / inbound-only
- no Edge direct DB
- strict firewall ports

## Default Port Recommendations

- Edge Local API: `7101`
- Link Ingress: `7201`
- Link Admin: `7202`
- Code API: `7301`
- Console Web: `7401`
- Console API: `7402`
- NexusAI API: `7501`
- PostgreSQL: `5432`
- Metrics: `9100+`
