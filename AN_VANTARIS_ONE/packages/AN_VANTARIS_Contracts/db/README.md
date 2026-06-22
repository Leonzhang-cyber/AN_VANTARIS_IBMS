# db

## Purpose

Documents DB contract boundaries and canonical-to-storage mapping rules.

## Authority role

Defines how DB implementation maps canonical contract semantics without becoming contract authority.

## What belongs here

- DB boundary policy docs
- canonical-to-DB mapping baselines
- contract-version to migration-metadata relationship guidance

## What must not be placed here

- executable migration scripts
- vendor-specific SQL implementation as authority contract
- direct EDGE/LINK database access patterns
