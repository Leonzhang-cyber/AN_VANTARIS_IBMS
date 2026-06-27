# Airport T3 Ground Floor POC Scenario Summary

## Scenario Objective

Demonstrate how VANTARIS ONE converts a real airport HMI floor map into an operational Data & Asset Map.

The POC should show that the system can connect:

- Real airport spaces
- Critical rooms
- System domains
- Assets
- Source tags
- Alarms
- Work orders
- Evidence requirements

## Main Demonstration Scenario

### Scenario 1: BHS Server Alarm

A critical BHS server alarm is triggered from the BHS Server Room.

Expected system behaviour:

1. Alarm appears in Faults & Events.
2. Alarm is located on the T3 Ground Floor map.
3. The affected space is identified as BHS Server Room.
4. The affected zone is Back of House.
5. The affected asset is BHS Application Server.
6. Operational impact is shown as possible baggage handling disruption.
7. A P1 work order is generated for BHS Engineer.
8. Evidence requirements are displayed for closure.

### Scenario 2: UPS On Battery

UPS alarm affects critical ICT/BHS rooms.

Expected system behaviour:

1. Alarm severity is critical.
2. Location is UPS Room.
3. Related systems include ICT, BHS, Security, and Comms.
4. Work order is assigned to Electrical Engineer.
5. Evidence includes UPS runtime, battery status, and incoming power status.

### Scenario 3: VIP Access Door Forced

VIP access control alarm is triggered.

Expected system behaviour:

1. Location is VIP Arrival Reception Lounge.
2. System domain is Access Control.
3. Operational impact is VIP area security risk.
4. Work order is assigned to Security Technician.
5. Evidence includes ACS event log, door status photo, and security confirmation.

## POC Success Criteria

- User can select T3 Ground Floor map.
- User can view zones and critical spaces.
- User can view assets by space.
- User can view point/tag bindings by asset.
- User can see alarms linked to space and asset.
- User can generate or view work orders from alarms.
- User can see required evidence for closure.
