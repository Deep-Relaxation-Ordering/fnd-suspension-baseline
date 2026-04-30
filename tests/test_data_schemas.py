"""FAIR metadata drift checks for committed notebook CSV artefacts."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "notebooks" / "data"
SCHEMA_DIR = DATA_DIR / "schemas"


def _load_schemas() -> list[dict[str, Any]]:
    schemas: list[dict[str, Any]] = []
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        with path.open() as fh:
            schema = json.load(fh)
        schema["_schema_path"] = path
        schemas.append(schema)
    return schemas


def _csv_path_for(schema: dict[str, Any]) -> Path:
    return (schema["_schema_path"].parent / schema["path"]).resolve()


def _parse_value(raw: str, field: dict[str, Any], missing_values: set[str]) -> object:
    constraints = field.get("constraints", {})
    required = constraints.get("required", True)
    if raw in missing_values:
        if required:
            raise AssertionError(f"{field['name']} is required but has a missing value")
        return None

    field_type = field["type"]
    if field_type == "number":
        value = float(raw)
        if not math.isfinite(value):
            raise AssertionError(f"{field['name']} is not finite: {raw!r}")
        return value
    if field_type == "integer":
        return int(raw)
    if field_type == "boolean":
        if raw not in {"True", "False", "true", "false"}:
            raise AssertionError(f"{field['name']} is not a boolean literal: {raw!r}")
        return raw.lower() == "true"
    if field_type == "string":
        return raw
    raise AssertionError(f"unsupported Frictionless field type {field_type!r}")


def _check_constraints(value: object, field: dict[str, Any]) -> None:
    if value is None:
        return

    constraints = field.get("constraints", {})
    if "enum" in constraints:
        assert value in constraints["enum"], (
            f"{field['name']} value {value!r} not in {constraints['enum']!r}"
        )
    if "minimum" in constraints:
        assert isinstance(value, int | float)
        assert value >= constraints["minimum"], (
            f"{field['name']} value {value!r} below {constraints['minimum']!r}"
        )
    if "maximum" in constraints:
        assert isinstance(value, int | float)
        assert value <= constraints["maximum"], (
            f"{field['name']} value {value!r} above {constraints['maximum']!r}"
        )


def test_every_csv_has_one_schema() -> None:
    csv_names = {path.name for path in DATA_DIR.glob("*.csv")}
    schema_csv_names = {_csv_path_for(schema).name for schema in _load_schemas()}

    assert schema_csv_names == csv_names


def test_declared_data_schemas_match_committed_csvs() -> None:
    for schema in _load_schemas():
        csv_path = _csv_path_for(schema)
        assert csv_path.is_file(), f"{schema['_schema_path']} points at missing {csv_path}"
        assert schema["$schema"].endswith("/table-schema.json")

        fields = schema["fields"]
        field_names = [field["name"] for field in fields]
        assert len(field_names) == len(set(field_names)), f"duplicate fields in {schema['name']}"
        missing_values = set(schema.get("missingValues", [""]))

        with csv_path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            assert reader.fieldnames == field_names
            row_count = 0
            for row in reader:
                row_count += 1
                for field in fields:
                    value = _parse_value(row[field["name"]], field, missing_values)
                    _check_constraints(value, field)

        assert row_count == schema["rowCount"], (
            f"{csv_path.name} row count changed: {row_count} != {schema['rowCount']}"
        )
