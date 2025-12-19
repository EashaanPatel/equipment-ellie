from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Checkout:
    id: UUID
    equipment_id: UUID
    person_id: UUID
    checked_out_at: datetime
    due_at: datetime
    checked_in_at: Optional[datetime] = None
    transferred_at: Optional[datetime] = None
    transferred_to_person_id: Optional[UUID] = None

    @property
    def is_active(self) -> bool:
        return self.checked_in_at is None and self.transferred_at is None
