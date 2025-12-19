from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Dict, List
from uuid import UUID

from equipment_ellie.models import Checkout


class CheckoutStore:
    def __init__(self) -> None:
        self._checkouts: Dict[UUID, Checkout] = {}

    def add(self, checkout: Checkout) -> None:
        self._checkouts[checkout.id] = checkout

    def list_for_equipment(self, equipment_id: UUID) -> List[Checkout]:
        return [
            checkout
            for checkout in self._checkouts.values()
            if checkout.equipment_id == equipment_id
        ]

    def active_for_equipment(self, equipment_id: UUID) -> Checkout | None:
        for checkout in self._checkouts.values():
            if checkout.equipment_id == equipment_id and checkout.is_active:
                return checkout
        return None

    def close_checkout(
        self,
        checkout: Checkout,
        *,
        checked_in_at: datetime,
        transferred_to_person_id: UUID | None = None,
    ) -> None:
        self._checkouts[checkout.id] = replace(
            checkout,
            checked_in_at=checked_in_at,
            transferred_at=checked_in_at if transferred_to_person_id else None,
            transferred_to_person_id=transferred_to_person_id,
        )
