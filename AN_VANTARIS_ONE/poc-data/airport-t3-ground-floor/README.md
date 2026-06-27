# VANTARIS ONE Airport T3 Ground Floor POC Data Pack

## Purpose

This data pack converts the customer-provided T3 Ground Floor HMI airport map into a structured POC dataset for VANTARIS ONE Data & Asset Map demonstration.

## Source

- Source drawing: W2-TE3-ARC-GROUND FLOOR LAYOUT PLAN Model.pdf
- Scope: Terminal 3 Ground Floor
- Use case: HMI base map, zone map, space registry, asset registry, point/tag binding, alarm/event simulation, work order routing

## Data Files

| File | Purpose |
|---|---|
| map_registry.csv | HMI base map metadata |
| zone_registry.csv | T3 Ground Floor zones |
| space_registry.csv | Critical spaces and rooms |
| asset_registry.csv | Assets mapped to spaces |
| point_tag_binding.csv | Source system tags mapped to assets and spaces |
| event_alarm_sample.csv | Sample alarms/events for POC |
| work_order_sample.csv | Sample work orders linked to events/assets/spaces |

## POC Flow

Airport Map  
→ Zone  
→ Space  
→ Asset  
→ Point / Tag  
→ Alarm / Event  
→ Work Order  
→ Evidence

## Initial Coverage

This first POC version covers:

- 1 HMI base map
- 7 operational zones
- 31 critical spaces
- 26 mapped assets
- 23 point/tag bindings
- 5 sample alarms/events
- 5 linked work orders

## Frozen Menu Mapping

No menu changes are required.

Primary menu placement:

Assets & Locations  
→ Floor Plan / HMI Map

Related areas:

- Assets & Locations → Asset Registry
- Assets & Locations → Point & Tag Governance
- Faults & Events → Alarm Console
- Work Management → Work Order Control
- Integration & Partner Hub → Industry Connectors
- Industry Solutions → Airport
- Reports & Documents → Export & Evidence Center

## Status

POC data v1.  
Relationship validation passed.  
Manual customer-space verification is still required before production import.
