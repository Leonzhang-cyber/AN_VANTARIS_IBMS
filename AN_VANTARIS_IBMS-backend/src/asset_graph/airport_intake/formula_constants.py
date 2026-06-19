"""Formula-safe constants for airport asset Excel intake."""
from __future__ import annotations

FORMULA_PROFILE_AUTHORITY = "ONE-AIRPORT-A1-01F"

APPROVED_FORMULA_COLUMNS = frozenset(
    {
        "SL",
        "Building",
        "Level",
        "Zone",
        "DA",
        "System",
        "Device Type",
    }
)

CONDITIONAL_FORMULA_COLUMNS = frozenset({"Day"})

ALLOWED_LEVEL_CODES = frozenset({"BAS", "GRD", "1ST", "2ND", "ROF"})

FORMULA_CLASSIFICATIONS = frozenset(
    {
        "APPROVED_DERIVED_FORMULA",
        "LEGACY_AMBIGUOUS_FORMULA",
        "LEGACY_FIELD_SEMANTIC_CONFLICT",
        "UNAPPROVED_FORMULA",
        "EXTERNAL_REFERENCE_FORMULA",
        "UNSUPPORTED_FORMULA",
        "FORMULA_CACHE_MISSING",
        "FORMULA_CACHE_MISSING_RECONSTRUCTED",
        "FORMULA_DERIVATION_MISMATCH",
        "NOT_A_FORMULA",
    }
)

FORBIDDEN_FORMULA_TOKENS = (
    "INDIRECT(",
    "OFFSET(",
    "WEBSERVICE(",
    "RTD(",
    "DDE(",
    "CUBE",
    "CALL(",
    "EXEC(",
    "REGISTER(",
)

EXTERNAL_FORMULA_MARKERS = (
    "HTTP://",
    "HTTPS://",
    "FILE://",
    "[HTTP",
    ".XLS]",
    ".XLSX]",
    ".XLSM]",
)

SAFE_FORMULA_FUNCTIONS = (
    "LEFT",
    "RIGHT",
    "MID",
    "TRIM",
    "UPPER",
    "LOWER",
    "IF",
    "FIND",
    "ISNUMBER",
    "COUNTA",
    "SUBSTITUTE",
    "REPT",
    "CONCATENATE",
    "LEN",
    "TEXT",
)

DEVICE_TYPE_CODE_HINTS = {
    "FCT": "Fixed Camera",
    "TEL": "IP Telephone",
    "SPK": "Speaker",
    "DRR": "Door Reader",
    "SEN": "Sensor",
    "PAN": "Panel",
    "CLK": "Clock",
    "SCN": "Scanner",
}

REAL_WORKBOOK_SHA256 = "60eac97282b1cae4d1697ad1b0505d66f530a638b3de3d095f9e5f9c620a3d48"

REAL_WORKBOOK_FORMULA_EVIDENCE = {
    "totalFormulaCells": 2905,
    "byWorksheet": {
        "Zone-1": 1037,
        "Zone-2": 1868,
    },
    "formulaColumnsByWorksheet": {
        "Zone-1": ["A", "C", "D", "E", "F", "G", "J"],
        "Zone-2": ["A", "C", "D", "E", "F", "G", "J", "K"],
    },
}
