"""Domain models for equipment checkouts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EquipmentStatus(str, Enum):
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"


@dataclass
class Equipment:
    """Represents a piece of equipment."""

    id: int
    name: str
    status: EquipmentStatus = EquipmentStatus.AVAILABLE


@dataclass
class Checkout:
    """Represents a checkout record for equipment."""

    id: int
    equipment_id: int
    checked_out_at: datetime
    due_at: datetime
    checked_in_at: Optional[datetime] = None
