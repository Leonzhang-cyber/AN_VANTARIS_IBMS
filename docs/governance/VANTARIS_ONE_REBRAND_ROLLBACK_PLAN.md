# VANTARIS ONE Rebrand Rollback Plan

## 1. Rollback Principle

- every phase separate commit
- no mixed runtime/DB/API rename
- tag before each runtime migration phase
- docs-only rebrand can be reverted by commit revert
- runtime migration requires backup branch/tag
- DB migration requires backup + migration rollback script
- API namespace change requires compatibility fallback

## 2. Rollback Levels

- Level 1 — docs-only rollback
- Level 2 — skeleton rollback
- Level 3 — package skeleton rollback
- Level 4 — runtime package migration rollback
- Level 5 — API namespace rollback
- Level 6 — DB migration rollback
- Level 7 — deployment rollback

## 3. Required Evidence Before Runtime Rename

- git clean
- source inventory
- target package boundary
- compatibility test
- build/test result
- backup tag
- rollback instructions
- owner approval

## 4. Forbidden Rollback Assumptions

- do not assume global replace can be safely reverted manually
- do not assume DB rename can be reverted without migration
- do not assume frontend routes remain compatible unless tested
- do not assume Edge/Link extraction is safe without source audit
