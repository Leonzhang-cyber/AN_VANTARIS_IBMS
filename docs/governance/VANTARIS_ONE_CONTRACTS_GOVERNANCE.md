# VANTARIS ONE Contracts Governance

## 1. Contracts Position

`AN_VANTARIS_Contracts` 是 VANTARIS ONE 的统一契约源头。  
Contracts 不是业务 runtime。  
Contracts 不直接连接 DB。  
Contracts 不直接调用 Edge / Link / Code / Console / NexusAI。  
Contracts 定义所有模块之间的 API、Event、Schema、Envelope、Error Code、Security、Module、Patch、License、DID/VC、CDE、AI 规则。

## 2. Contract Ownership

- Object Model
- API Contracts
- Event Contracts
- Edge/Link Envelope Contracts
- Protocol Contracts
- Security Contracts
- Module Manifest Contracts
- Patch Manifest Contracts
- License VC Contracts
- DID / VC Contracts
- CDE Contracts
- AI Request / Response Contracts
- DB Schema Contract Reference
- Error / Status Code Contracts
- Port / Network Boundary Contracts
- Versioning Contracts

## 3. Contract Change Rules

- contract-first change
- semantic versioning
- backward compatibility required for public APIs
- breaking change must create new version
- generated files must be traceable to source contract
- runtime modules must not invent private cross-module schema
- Edge/Link/Code/Console/NexusAI/DB must align to Contracts
- DB table rename only after migration contract
- API namespace change only after contract approval
- UFMS integration only through approved adapter contract

## 4. Contract Review Gates

- Architecture review
- Security review
- Runtime owner review
- DB migration review
- Backward compatibility review
- Evidence/audit review
