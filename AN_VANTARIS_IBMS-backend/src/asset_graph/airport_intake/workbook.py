"""Read-only airport asset Excel workbook access."""
from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any, Mapping
from xml.etree import ElementTree as ET

from .constants import BUSINESS_WORKSHEETS, MAX_SOURCE_ROWS, REQUIRED_WORKSHEETS
from .errors import AirportIntakeError
from .headers import normalize_header, normalize_headers

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
_REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
_OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_FORMULA_RE = re.compile(r"^[=+\-@]")


class AirportExcelWorkbook:
    """Minimal read-only .xlsx accessor for airport asset master workbooks."""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        self._archive = zipfile.ZipFile(self.path, "r")
        self._shared_strings = self._load_shared_strings()
        self._sheet_map = self._load_sheet_map()

    def close(self) -> None:
        self._archive.close()

    def __enter__(self) -> "AirportExcelWorkbook":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @staticmethod
    def validate_extension(path: Path) -> None:
        suffix = path.suffix.lower()
        if suffix == ".xlsx":
            return
        if suffix in {".xls", ".xlsm", ".xlsb"}:
            raise AirportIntakeError("UNSUPPORTED_EXTENSION", f"unsupported workbook extension: {suffix}")
        raise AirportIntakeError("UNSUPPORTED_EXTENSION", "only .xlsx workbooks are accepted")

    @staticmethod
    def open(path: Path) -> "AirportExcelWorkbook":
        resolved = path.resolve()
        AirportExcelWorkbook.validate_extension(resolved)
        if not resolved.is_file():
            raise AirportIntakeError("WORKBOOK_NOT_FOUND", "workbook file was not found")
        try:
            book = AirportExcelWorkbook(resolved)
        except zipfile.BadZipFile as exc:
            raise AirportIntakeError("INVALID_WORKBOOK", "workbook is not a valid xlsx archive") from exc
        if book.has_macros():
            book.close()
            raise AirportIntakeError("MACROS_NOT_ALLOWED", "macro-enabled workbook content is not accepted")
        if book.is_password_protected():
            book.close()
            raise AirportIntakeError("PASSWORD_PROTECTED", "password-protected workbooks are not accepted")
        if book.has_external_links():
            book.close()
            raise AirportIntakeError("EXTERNAL_LINKS", "external workbook links are not accepted")
        if book.has_hidden_binary_payload():
            book.close()
            raise AirportIntakeError("HIDDEN_BINARY_PAYLOAD", "hidden binary payloads are not accepted")
        missing = [name for name in REQUIRED_WORKSHEETS if name not in book.sheet_names()]
        if missing:
            book.close()
            raise AirportIntakeError("MISSING_WORKSHEET", f"required worksheets missing: {', '.join(missing)}")
        return book

    def sheet_names(self) -> tuple[str, ...]:
        return tuple(self._sheet_map)

    def rows_with_row_numbers(self, sheet_name: str) -> list[tuple[int, dict[str, Any]]]:
        if sheet_name not in self._sheet_map:
            raise AirportIntakeError("MISSING_WORKSHEET", f"worksheet not found: {sheet_name}")
        xml_path = self._sheet_map[sheet_name]
        root = ET.fromstring(self._archive.read(xml_path))
        table: dict[int, dict[int, Any]] = {}
        formulas: set[str] = set()
        for row in root.findall("m:sheetData/m:row", _NS):
            row_index = int(row.attrib.get("r", "0"))
            for cell in row.findall("m:c", _NS):
                ref = cell.attrib.get("r", "")
                col_index = _column_index(ref)
                if cell.find("m:f", _NS) is not None:
                    formulas.add(f"{sheet_name}!{ref}")
                value = self._cell_value(cell)
                if value is not None and isinstance(value, str) and _FORMULA_RE.match(value.strip()):
                    formulas.add(f"{sheet_name}!{ref}")
                table.setdefault(row_index, {})[col_index] = value
        if sheet_name in BUSINESS_WORKSHEETS and formulas:
            raise AirportIntakeError("FORMULAS_NOT_ALLOWED", "formulas are not allowed in business worksheets")
        if not table:
            return []
        header_row_index = min(table)
        header_row = table[header_row_index]
        raw_headers = [_stringify(header_row.get(idx, "")) for idx in sorted(header_row)]
        headers = normalize_headers(raw_headers)
        if any(not header for header in headers):
            raise AirportIntakeError("EMPTY_HEADER", f"worksheet {sheet_name} contains empty header cells")
        if len(headers) != len(set(headers)):
            raise AirportIntakeError("DUPLICATE_HEADERS", f"worksheet {sheet_name} contains duplicate headers")
        records: list[tuple[int, dict[str, Any]]] = []
        for row_index in sorted(index for index in table if index > header_row_index):
            values = table[row_index]
            record = {
                headers[col - 1]: values.get(col)
                for col in sorted(values)
                if col - 1 < len(headers)
            }
            if _row_has_data(record):
                records.append((row_index, record))
        if len(records) > MAX_SOURCE_ROWS:
            raise AirportIntakeError("EXCESSIVE_ROW_COUNT", f"worksheet {sheet_name} exceeds row policy")
        return records

    def has_macros(self) -> bool:
        return any(name.startswith("xl/vbaProject") for name in self._archive.namelist())

    def is_password_protected(self) -> bool:
        try:
            root = ET.fromstring(self._archive.read("xl/workbook.xml"))
        except KeyError:
            return False
        node = root.find("m:workbookProtection", _NS)
        if node is None:
            return False
        for attr in ("lockStructure", "lockWindows", "lockRevision", "workbookPassword", "revisionsPassword"):
            value = node.attrib.get(attr)
            if value and value not in {"0", "false", "False"}:
                return True
        return False

    def has_external_links(self) -> bool:
        for name in self._archive.namelist():
            if name.startswith("xl/externalLinks/"):
                return True
        rel_path = "xl/_rels/workbook.xml.rels"
        if rel_path not in self._archive.namelist():
            return False
        root = ET.fromstring(self._archive.read(rel_path))
        for rel in root.findall(f"{_REL_NS}Relationship"):
            target = rel.attrib.get("Target", "")
            rel_type = rel.attrib.get("Type", "")
            if "externalLink" in rel_type or target.startswith("file:") or target.startswith("../external"):
                return True
        return False

    def has_hidden_binary_payload(self) -> bool:
        suspicious = ("xl/embeddings/", "xl/activeX/", "xl/customData/")
        return any(name.startswith(prefix) for name in self._archive.namelist() for prefix in suspicious)

    def _load_shared_strings(self) -> list[str]:
        path = "xl/sharedStrings.xml"
        if path not in self._archive.namelist():
            return []
        root = ET.fromstring(self._archive.read(path))
        values: list[str] = []
        for item in root.findall("m:si", _NS):
            text_parts = [node.text or "" for node in item.findall(".//m:t", _NS)]
            values.append("".join(text_parts))
        return values

    def _load_sheet_map(self) -> dict[str, str]:
        workbook = ET.fromstring(self._archive.read("xl/workbook.xml"))
        rels = ET.fromstring(self._archive.read("xl/_rels/workbook.xml.rels"))
        rel_targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall(f"{_REL_NS}Relationship")
        }
        mapping: dict[str, str] = {}
        for sheet in workbook.findall("m:sheets/m:sheet", _NS):
            name = sheet.attrib["name"]
            rel_id = sheet.attrib.get(f"{{{_OFFICE_REL}}}id")
            target = rel_targets.get(rel_id or "", "")
            if target.startswith("/"):
                target = target.lstrip("/")
            elif not target.startswith("xl/"):
                target = f"xl/{target}"
            mapping[name] = target
        return mapping

    def _cell_value(self, cell: ET.Element) -> Any:
        cell_type = cell.attrib.get("t")
        if cell_type == "inlineStr":
            node = cell.find("m:is/m:t", _NS)
            return node.text if node is not None else ""
        if cell_type == "s":
            value_node = cell.find("m:v", _NS)
            if value_node is None or value_node.text is None:
                return ""
            index = int(value_node.text)
            return self._shared_strings[index] if 0 <= index < len(self._shared_strings) else ""
        if cell_type == "b":
            value_node = cell.find("m:v", _NS)
            return value_node is not None and value_node.text == "1"
        value_node = cell.find("m:v", _NS)
        if value_node is None or value_node.text is None:
            return None
        text = value_node.text
        if cell_type == "str":
            return text
        try:
            if "." in text:
                return float(text)
            return int(text)
        except ValueError:
            return text


def _column_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    index = 0
    for char in letters:
        index = index * 26 + (ord(char.upper()) - 64)
    return index


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _row_has_data(record: Mapping[str, Any]) -> bool:
    return any(value not in (None, "") for value in record.values())
