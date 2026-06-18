# ONE Adapter Consumer Contract Draft

## 1. Purpose

This document defines the ONE Adapter A1/A2 consumer contract draft as a docs-level boundary.
It describes how VANTARIS ONE consumes shared foundation references without owning foundation runtime.

## 2. Scope

- docs-level consumer boundary only
- reference mapping and consumption policy draft only
- no runtime adapter implementation
- no API implementation
- no real schema definition

## 3. Foundation Relationship

ONE Adapter consumes references from `AN_VANTARIS_Contracts`, `AN_VANTARIS_EDGE`, `AN_VANTARIS_LINK`, and `AN_VANTARIS_DB` in reference-only mode.

## 4. Business Module Consumption Route

UCore, UMMS, UESG, UCDE, and UDOC consume foundation references through ONE Adapter boundary definitions.

## 5. A1/A2 Boundary

This draft does not modify `AN_VANTARIS_Contracts`, `contracts/`, `schemas/`, backend, frontend, or runtime code.
A2 remains gate/design planning only and does not authorize implementation.
