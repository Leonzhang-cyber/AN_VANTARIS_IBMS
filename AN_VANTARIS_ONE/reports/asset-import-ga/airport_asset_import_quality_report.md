# Airport Asset Import Data Quality Report

## Production Import Readiness

- Readiness: **HOLD_BLOCKED**
- Confirm enabled: False
- Requires second confirmation: True

## Summary

- total_records: 5187
- source_files: ['Asset Database Zonewise_Basement_SH_030626.xlsx', 'Asset Database Zonewise_Ground Floor_SH_220626.xlsx']
- sheet_count: 8
- level_count: 4
- zone_count: 8
- system_count: 7
- device_type_count: 78
- location_count: 406
- blocker_count: 2
- major_count: 1
- warning_count: 7
- info_count: 0
- readiness: HOLD_BLOCKED

## Source Files

- Asset Database Zonewise_Basement_SH_030626.xlsx: 470 records, sha256=d20f788a82f6fa8382e90079d64a6c12d8b67cc9b2073906977677c06ab7dfa3
- Asset Database Zonewise_Ground Floor_SH_220626.xlsx: 4717 records, sha256=980fad9d423deeec4a017c421d1870e1b0208340b917d47e1cf7215b6ac2b322

## Issue Summary

- BLOCKER: 2
- MAJOR: 1
- WARNING: 7
- INFO: 0

## Import Alert Payload

```json
{
  "title": "Asset Import Quality Check",
  "message": "Customer asset workbook has been parsed and validated. Review the quality report before import.",
  "readiness": "HOLD_BLOCKED",
  "confirm_enabled": false,
  "requires_review": true,
  "requires_second_confirmation": true,
  "action_labels": [
    "Cancel Import",
    "Download Quality Report",
    "Review Issues",
    "Confirm Import"
  ]
}
```

## Issues

### MAJOR / required_field
- Missing required field: Location
- Count: 31
- Sample:
```json
[
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-1",
    "row": 278,
    "SL": "277",
    "Device ID": "TE3-PAS-GRD-DA11-NOS-001",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z1",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  },
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-1",
    "row": 279,
    "SL": "278",
    "Device ID": "TE3-PAS-GRD-DA11-NOS-002",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z1",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  },
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-2",
    "row": 665,
    "SL": "664",
    "Device ID": "TE3-PAS-GRD-DA22-NOS-001",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z2",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  },
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-2",
    "row": 666,
    "SL": "665",
    "Device ID": "TE3-PAS-GRD-DA22-NOS-002",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z2",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  },
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-2",
    "row": 667,
    "SL": "666",
    "Device ID": "TE3-PAS-GRD-DA22-NOS-003",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z2",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  },
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-2",
    "row": 668,
    "SL": "667",
    "Device ID": "TE3-PAS-GRD-DA22-NOS-005",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z2",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  },
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-2",
    "row": 669,
    "SL": "668",
    "Device ID": "TE3-PAS-GRD-DA22-NOS-006",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z2",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  },
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-2",
    "row": 670,
    "SL": "669",
    "Device ID": "TE3-PAS-GRD-DA22-NOS-007",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z2",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  },
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-3",
    "row": 909,
    "SL": "908",
    "Device ID": "TE3-PAS-GRD-DA21-NOS-001",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z3",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  },
  {
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-3",
    "row": 910,
    "SL": "909",
    "Device ID": "TE3-PAS-GRD-DA21-NOS-002",
    "Building": "TE3",
    "Level": "GRD",
    "Zone": "Z3",
    "System": "PA",
    "Location": "",
    "Device Type": "Noise Sensor"
  }
]
```
### BLOCKER / duplicate_device_id
- Duplicate Device ID detected
- Count: 40
- Sample:
```json
[
  {
    "Device ID": "TE3-PAS-BAS-DA21-HSP-032",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 145,
    "System": "PA",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Horn Speaker"
  },
  {
    "Device ID": "TE3-PAS-BAS-DA21-HSP-032",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-2",
    "row": 138,
    "System": "PA",
    "Location": "BASEMET SERVICE ROAD",
    "Device Type": "Horn Speaker"
  },
  {
    "Device ID": "TE3-PAS-BAS-DA31-HSP-030",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 161,
    "System": "PA",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Horn Speaker"
  },
  {
    "Device ID": "TE3-PAS-BAS-DA31-HSP-030",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-2",
    "row": 234,
    "System": "PA",
    "Location": "BASEMET SERVICE ROAD",
    "Device Type": "Horn Speaker"
  },
  {
    "Device ID": "TE3-PAS-BAS-DA31-HSP-031",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 162,
    "System": "PA",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Horn Speaker"
  },
  {
    "Device ID": "TE3-PAS-BAS-DA31-HSP-031",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-2",
    "row": 235,
    "System": "PA",
    "Location": "BASEMET SERVICE ROAD",
    "Device Type": "Horn Speaker"
  },
  {
    "Device ID": "TE3-PAS-BAS-DA31-HSP-032",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 163,
    "System": "PA",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Horn Speaker"
  },
  {
    "Device ID": "TE3-PAS-BAS-DA31-HSP-032",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-2",
    "row": 236,
    "System": "PA",
    "Location": "BASEMET SERVICE ROAD",
    "Device Type": "Horn Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-024",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 164,
    "System": "PA",
    "Location": "STC-E14",
    "Device Type": "Box Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-024",
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-2",
    "row": 326,
    "System": "PA",
    "Location": "STC-E11",
    "Device Type": "Box Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-025",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 165,
    "System": "PA",
    "Location": "STC-E14",
    "Device Type": "Box Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-025",
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-3",
    "row": 462,
    "System": "PA",
    "Location": "BAGGAGE BREAKDOWN",
    "Device Type": "Box Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-026",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 166,
    "System": "PA",
    "Location": "STC-E5",
    "Device Type": "Box Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-026",
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-3",
    "row": 463,
    "System": "PA",
    "Location": "BAGGAGE BREAKDOWN",
    "Device Type": "Box Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-027",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 167,
    "System": "PA",
    "Location": "STC-E3",
    "Device Type": "Box Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-027",
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-3",
    "row": 464,
    "System": "PA",
    "Location": "BAGGAGE BREAKDOWN",
    "Device Type": "Box Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-PSP-001",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 169,
    "System": "PA",
    "Location": "STC-E3",
    "Device Type": "Projection Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-PSP-001",
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-3",
    "row": 914,
    "System": "PA",
    "Location": "GENERAL AREA",
    "Device Type": "Projection Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-PSP-002",
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 170,
    "System": "PA",
    "Location": "STC-E3",
    "Device Type": "Projection Speaker"
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-PSP-002",
    "source_file": "Asset Database Zonewise_Ground Floor_SH_220626.xlsx",
    "sheet": "Zone-3",
    "row": 915,
    "System": "PA",
    "Location": "GENERAL AREA",
    "Device Type": "Projection Speaker"
  }
]
```
### BLOCKER / duplicate_conflict
- Duplicate Device ID has conflicting attributes
- Count: 38
- Sample:
```json
[
  {
    "Device ID": "TE3-PAS-BAS-DA21-HSP-032",
    "conflicts": {
      "Location": [
        "BASEMENT SERVICE ROAD",
        "BASEMET SERVICE ROAD"
      ],
      "Zone": [
        "Z1",
        "Z2"
      ]
    }
  },
  {
    "Device ID": "TE3-PAS-BAS-DA31-HSP-030",
    "conflicts": {
      "Location": [
        "BASEMENT SERVICE ROAD",
        "BASEMET SERVICE ROAD"
      ],
      "Zone": [
        "Z1",
        "Z2"
      ]
    }
  },
  {
    "Device ID": "TE3-PAS-BAS-DA31-HSP-031",
    "conflicts": {
      "Location": [
        "BASEMENT SERVICE ROAD",
        "BASEMET SERVICE ROAD"
      ],
      "Zone": [
        "Z1",
        "Z2"
      ]
    }
  },
  {
    "Device ID": "TE3-PAS-BAS-DA31-HSP-032",
    "conflicts": {
      "Location": [
        "BASEMENT SERVICE ROAD",
        "BASEMET SERVICE ROAD"
      ],
      "Zone": [
        "Z1",
        "Z2"
      ]
    }
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-024",
    "conflicts": {
      "Location": [
        "STC-E11",
        "STC-E14"
      ],
      "Zone": [
        "Z1",
        "Z2"
      ]
    }
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-025",
    "conflicts": {
      "Location": [
        "BAGGAGE BREAKDOWN",
        "STC-E14"
      ],
      "Zone": [
        "Z1",
        "Z3"
      ]
    }
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-026",
    "conflicts": {
      "Location": [
        "BAGGAGE BREAKDOWN",
        "STC-E5"
      ],
      "Zone": [
        "Z1",
        "Z3"
      ]
    }
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-BSP-027",
    "conflicts": {
      "Location": [
        "BAGGAGE BREAKDOWN",
        "STC-E3"
      ],
      "Zone": [
        "Z1",
        "Z3"
      ]
    }
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-PSP-001",
    "conflicts": {
      "Location": [
        "GENERAL AREA",
        "STC-E3"
      ],
      "Zone": [
        "Z1",
        "Z3"
      ]
    }
  },
  {
    "Device ID": "TE3-PAS-GRD-DA21-PSP-002",
    "conflicts": {
      "Location": [
        "GENERAL AREA",
        "STC-E3"
      ],
      "Zone": [
        "Z1",
        "Z3"
      ]
    }
  }
]
```
### WARNING / maintenance_field
- Missing maintenance field: Last Done
- Count: 5187
- Sample:
```json
[
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 2,
    "SL": "1",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-001",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "FIRE EXIT CORRIDOR",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 3,
    "SL": "2",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-002",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT STC E-14",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 4,
    "SL": "3",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-003",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 5,
    "SL": "4",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-004",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 6,
    "SL": "5",
    "Device ID": "TE3-CCT-BAS-DA21-PCT-005",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "PTZ Camera"
  }
]
```
### WARNING / maintenance_field
- Missing maintenance field: Due Date
- Count: 5187
- Sample:
```json
[
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 2,
    "SL": "1",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-001",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "FIRE EXIT CORRIDOR",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 3,
    "SL": "2",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-002",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT STC E-14",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 4,
    "SL": "3",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-003",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 5,
    "SL": "4",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-004",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 6,
    "SL": "5",
    "Device ID": "TE3-CCT-BAS-DA21-PCT-005",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "PTZ Camera"
  }
]
```
### WARNING / maintenance_field
- Missing maintenance field: Status
- Count: 5187
- Sample:
```json
[
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 2,
    "SL": "1",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-001",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "FIRE EXIT CORRIDOR",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 3,
    "SL": "2",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-002",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT STC E-14",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 4,
    "SL": "3",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-003",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 5,
    "SL": "4",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-004",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 6,
    "SL": "5",
    "Device ID": "TE3-CCT-BAS-DA21-PCT-005",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "PTZ Camera"
  }
]
```
### WARNING / maintenance_field
- Missing maintenance field: Overdue
- Count: 5187
- Sample:
```json
[
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 2,
    "SL": "1",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-001",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "FIRE EXIT CORRIDOR",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 3,
    "SL": "2",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-002",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT STC E-14",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 4,
    "SL": "3",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-003",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 5,
    "SL": "4",
    "Device ID": "TE3-CCT-BAS-DA21-FCT-004",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "Fixed Camera"
  },
  {
    "source_file": "Asset Database Zonewise_Basement_SH_030626.xlsx",
    "sheet": "Zone-1",
    "row": 6,
    "SL": "5",
    "Device ID": "TE3-CCT-BAS-DA21-PCT-005",
    "Building": "TE3",
    "Level": "BAS",
    "Zone": "Z1",
    "System": "CCTV",
    "Location": "BASEMENT SERVICE ROAD",
    "Device Type": "PTZ Camera"
  }
]
```
### WARNING / optional_field
- Empty optional field: Area
- Count: 5187
### WARNING / optional_field
- Empty optional field: Remarks
- Count: 5187
### WARNING / location_normalization
- Location naming normalization suggestions detected
- Count: 32
- Sample:
```json
[
  {
    "location": "BAGGAGE MARKUP",
    "suggested": "BAGGAGE MAKEUP"
  },
  {
    "location": "BAGGAGE RECON RM",
    "suggested": "BAGGAGE RECON ROOM"
  },
  {
    "location": "BAGGAGE RECONCILIATION RM",
    "suggested": "BAGGAGE RECONCILIATION ROOM"
  },
  {
    "location": "BAGGAGE SCREENING RM",
    "suggested": "BAGGAGE SCREENING ROOM"
  },
  {
    "location": "BASEMET SERVICE ROAD",
    "suggested": "BASEMENT SERVICE ROAD"
  },
  {
    "location": "BHS CONTROL & BHS CCTV RM",
    "suggested": "BHS CONTROL AND BHS CCTV ROOM"
  },
  {
    "location": "BHS CONTROL & BHS CCTV ROOM",
    "suggested": "BHS CONTROL AND BHS CCTV ROOM"
  },
  {
    "location": "BHS MAINTENANCE RM",
    "suggested": "BHS MAINTENANCE ROOM"
  },
  {
    "location": "C RM",
    "suggested": "C ROOM"
  },
  {
    "location": "COMMS & SECURITY EQPT STORAGE ROOM",
    "suggested": "COMMS AND SECURITY EQPT STORAGE ROOM"
  },
  {
    "location": "EAST REMOTE DEPT GATE LOUNGE",
    "suggested": "EAST REMOTE DEPARTURE GATE LOUNGE"
  },
  {
    "location": "EAST REMOTE DEPT GATE LOUNGE DOOR",
    "suggested": "EAST REMOTE DEPARTURE GATE LOUNGE DOOR"
  },
  {
    "location": "EQPT RM",
    "suggested": "EQPT ROOM"
  },
  {
    "location": "F&B",
    "suggested": "FANDB"
  },
  {
    "location": "FAN RM",
    "suggested": "FAN ROOM"
  },
  {
    "location": "FIRE TANK & PUMPS ROOM",
    "suggested": "FIRE TANK AND PUMPS ROOM"
  },
  {
    "location": "FIRE TANK & PUMPS ROOM DOOR",
    "suggested": "FIRE TANK AND PUMPS ROOM DOOR"
  },
  {
    "location": "FIRE TANKS & PUMPS ROOM",
    "suggested": "FIRE TANKS AND PUMPS ROOM"
  },
  {
    "location": "FIRE TANKS AND PUMPS RM",
    "suggested": "FIRE TANKS AND PUMPS ROOM"
  },
  {
    "location": "LANDSIDE WASTE DISPOSAL RM",
    "suggested": "LANDSIDE WASTE DISPOSAL ROOM"
  },
  {
    "location": "LOST & FOUND BAGGAGE SERVICES",
    "suggested": "LOST AND FOUND BAGGAGE SERVICES"
  },
  {
    "location": "MEETERS & GREETERS HALL",
    "suggested": "MEETERS AND GREETERS HALL"
  },
  {
    "location": "MEETERS-GREETERS HALL",
    "suggested": "MEETERS GREETERS HALL"
  },
  {
    "location": "P RM",
    "suggested": "P ROOM"
  },
  {
    "location": "PLB EQUIPMENT RM",
    "suggested": "PLB EQUIPMENT ROOM"
  },
  {
    "location": "PRAYER RM",
    "suggested": "PRAYER ROOM"
  },
  {
    "location": "PUMPS, CHILLER PLANT & CHILLERS",
    "suggested": "PUMPS, CHILLER PLANT AND CHILLERS"
  },
  {
    "location": "STAFF ENTRY & EXIT",
    "suggested": "STAFF ENTRY AND EXIT"
  },
  {
    "location": "STAFF ENTRY & EXIT CORRIDOR",
    "suggested": "STAFF ENTRY AND EXIT CORRIDOR"
  },
  {
    "location": "WATER TANK & PUMPS ROOM DOOR",
    "suggested": "WATER TANK AND PUMPS ROOM DOOR"
  }
]
```

## Top Systems

- PA: 2553
- ACS: 989
- CCTV: 878
- TEL: 614
- RAS: 68
- IPTV: 63
- MCS: 22

## Top Device Types

- Ceiling Speaker: 1941
- Fixed Camera: 702
- IP Telephone: 581
- Electro Magnetic Lock: 327
- Horn Speaker: 213
- Intelligent Controller: 197
- Emergency Break Glass: 189
- Box Speaker: 141
- IN Card Reader: 123
- PTZ Camera: 107
- Amplifier: 70
- Push Button: 55
- OUT Card Reader: 52
- Radio Antenna: 49
- Projection Speaker: 49
- Line Array Speaker: 44
- Noise Sensor: 36
- Workstation: 33
- CCTV Decoder: 22
- STB+TV: 19
- Turnstile: 18
- Key Switch: 16
- NVR: 13
- Standby Amplifier: 12
- Omneo Interface: 11
- Network Controller: 11
- 2-Way Splitter: 10
- Standard Call Station: 10
- SINGLE SIDED SLAVE CLOCK: 9
- Media Converter: 8
- FRS Server: 8
- 8-Way Splitter: 8
- Maestro Server: 7
- 3-Way Splitter: 6
- Basic Call Station: 6
- FO Receiver: 6
- DOUBLE SIDED SLAVE CLOCK: 4
- ISDN GATEWAY: 4
- Server: 4
- 4-Way Splitter: 4

## Top Locations

- BAGGAGE CLAIM HALL: 348
- BHS AREA: 274
- BAGGAGE CLAIM AREA: 230
- OFFICE: 193
- WEST REMOTE DEPARTURE GATE LOUNGE: 125
- DA ROOM: 117
- ARRIVAL KERBSIDE: 109
- MEETERS GREETERS HALL: 106
- AIRPORT OPERATION CENTER: 105
- EAST REMOTE DEPARTURE GATE LOUNGE: 103
- COMMS EQUIPMENT ROOM - 1: 88
- SECURITY CONTROL ROOM: 85
- VIP KERBSIDE: 79
- BAGGAGE BREAKDOWN: 77
- BAGGAGE MAKEUP: 75
- DUTY FREE: 68
- EAST REMOTE DEPT GATE LOUNGE: 64
- OFFICE 92: 59
- OFFICE 88: 57
- MEETERS AND GREETERS HALL: 54
- UPS ROOM: 50
- CUSTOMS OFFICE: 49
- STAFF ENTRY: 49
- LT ROOM: 46
- BAGGAGE MARKUP: 45
- OFFICE 56: 44
- TOURIST SERVICE COUNTERS: 43
- REMOTE ARRIVAL LOUNGE: 42
- CUSTOMS: 40
- REMOTE ARRIVALS LOUNGE: 40
- BAGGAGE MAKEUP AREA: 37
- MEETERS-GREETERS HALL: 36
- CUSTOM AREA: 36
- BASEMENT SERVICE ROAD: 35
- STAFF ENTRY & EXIT: 33
- WEST REMOTE DEPARTURE GATE: 32
- TX ROOM: 31
- M (PAX): 31
- (blank): 31
- SECURITY CHECK AREA: 30