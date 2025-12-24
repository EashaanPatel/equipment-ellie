"""Equipment Ellie application entry point and storage utilities."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict


SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Equipment Ellie Data",
    "type": "object",
    "additionalProperties": False,
    "required": ["equipment", "people", "checkouts"],
    "properties": {
        "equipment": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "name", "status"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
        },
        "people": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "name"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                },
            },
        },
        "checkouts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "equipment_id",
                    "person_id",
                    "checked_out_at",
                    "due_at",
                    "checked_in_at",
                ],
                "properties": {
                    "equipment_id": {"type": "string"},
                    "person_id": {"type": "string"},
                    "checked_out_at": {"type": "string", "format": "date-time"},
                    "due_at": {"type": "string", "format": "date-time"},
                    "checked_in_at": {
                        "type": ["string", "null"],
                        "format": "date-time",
                    },
                },
            },
        },
    },
}


def default_data() -> Dict[str, Any]:
    """Return a new empty data structure matching the schema."""
    return {"equipment": [], "people": [], "checkouts": []}


def load_data(path: str) -> Dict[str, Any]:
    """Load data from a JSON file.

    Returns a default structure if the file does not exist.
    """
    if not os.path.exists(path):
        return default_data()
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_data(path: str, data: Dict[str, Any]) -> None:
    """Atomically save data to a JSON file.

    Writes to a temporary file in the same directory before replacing the target.
    """
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=directory) as tmp:
        json.dump(data, tmp, indent=2, sort_keys=True)
        tmp.write("\n")
        temp_name = tmp.name
    os.replace(temp_name, path)


def main() -> None:
    """Simple entry point to initialize data storage."""
    data_path = os.environ.get("EQUIPMENT_ELLIE_DATA", "equipment_data.json")
    data = load_data(data_path)
    save_data(data_path, data)
    print(f"Data stored at {data_path}")


if __name__ == "__main__":
    main()
