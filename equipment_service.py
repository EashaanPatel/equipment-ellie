import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from storage import JsonStore


class ValidationError(ValueError):
    pass


@dataclass
class EquipmentService:
    store: JsonStore

    def list_equipment(self) -> List[Dict[str, Any]]:
        data = self.store.load()
        return list(data.get("equipment", []))

    def get_equipment(self, equipment_id: str) -> Dict[str, Any]:
        equipment = self._find_equipment(equipment_id)
        if equipment is None:
            raise KeyError(f"Equipment '{equipment_id}' not found")
        return equipment

    def add_equipment(
        self,
        name: str,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_field("name", name)
        data = self.store.load()
        equipment = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "status": status,
        }
        data.setdefault("equipment", []).append(equipment)
        self.store.save(data)
        return equipment

    def update_equipment(
        self,
        equipment_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        if name is None and description is None and status is None:
            raise ValidationError("At least one field must be provided to update equipment")
        data = self.store.load()
        equipment = self._find_equipment(equipment_id, data)
        if equipment is None:
            raise KeyError(f"Equipment '{equipment_id}' not found")
        if name is not None:
            self._require_field("name", name)
            equipment["name"] = name
        if description is not None:
            equipment["description"] = description
        if status is not None:
            equipment["status"] = status
        self.store.save(data)
        return equipment

    def delete_equipment(self, equipment_id: str) -> None:
        data = self.store.load()
        equipment = self._find_equipment(equipment_id, data)
        if equipment is None:
            raise KeyError(f"Equipment '{equipment_id}' not found")
        data["equipment"] = [
            item for item in data.get("equipment", []) if item["id"] != equipment_id
        ]
        self.store.save(data)

    def _find_equipment(
        self, equipment_id: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if data is None:
            data = self.store.load()
        for equipment in data.get("equipment", []):
            if equipment.get("id") == equipment_id:
                return equipment
        return None

    @staticmethod
    def _require_field(field_name: str, value: Optional[str]) -> None:
        if value is None or not str(value).strip():
            raise ValidationError(f"Field '{field_name}' is required")
