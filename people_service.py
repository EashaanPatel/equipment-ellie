import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from storage import JsonStore


class ValidationError(ValueError):
    pass


@dataclass
class PeopleService:
    store: JsonStore

    def list_people(self) -> List[Dict[str, Any]]:
        data = self.store.load()
        return list(data.get("people", []))

    def get_person(self, person_id: str) -> Dict[str, Any]:
        person = self._find_person(person_id)
        if person is None:
            raise KeyError(f"Person '{person_id}' not found")
        return person

    def add_person(
        self,
        name: str,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._require_field("name", name)
        data = self.store.load()
        person = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "role": role,
        }
        data.setdefault("people", []).append(person)
        self.store.save(data)
        return person

    def update_person(
        self,
        person_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        if name is None and email is None and role is None:
            raise ValidationError("At least one field must be provided to update a person")
        data = self.store.load()
        person = self._find_person(person_id, data)
        if person is None:
            raise KeyError(f"Person '{person_id}' not found")
        if name is not None:
            self._require_field("name", name)
            person["name"] = name
        if email is not None:
            person["email"] = email
        if role is not None:
            person["role"] = role
        self.store.save(data)
        return person

    def delete_person(self, person_id: str) -> None:
        data = self.store.load()
        person = self._find_person(person_id, data)
        if person is None:
            raise KeyError(f"Person '{person_id}' not found")
        data["people"] = [item for item in data.get("people", []) if item["id"] != person_id]
        self.store.save(data)

    def _find_person(
        self, person_id: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if data is None:
            data = self.store.load()
        for person in data.get("people", []):
            if person.get("id") == person_id:
                return person
        return None

    @staticmethod
    def _require_field(field_name: str, value: Optional[str]) -> None:
        if value is None or not str(value).strip():
            raise ValidationError(f"Field '{field_name}' is required")
