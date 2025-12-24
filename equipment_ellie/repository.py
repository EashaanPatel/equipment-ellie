"""Repositories for storing checkout records."""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Optional

from .models import Checkout


class CheckoutRepository:
    """In-memory repository for checkout records."""

    def __init__(self) -> None:
        self._checkouts: Dict[int, Checkout] = {}
        self._next_id = 1

    def create(self, checkout: Checkout) -> Checkout:
        checkout_with_id = replace(checkout, id=self._next_id)
        self._checkouts[self._next_id] = checkout_with_id
        self._next_id += 1
        return checkout_with_id

    def get_active_for_equipment(self, equipment_id: int) -> Optional[Checkout]:
        return next(
            (
                checkout
                for checkout in self._checkouts.values()
                if checkout.equipment_id == equipment_id
                and checkout.checked_in_at is None
            ),
            None,
        )

    def update(self, checkout: Checkout) -> None:
        if checkout.id not in self._checkouts:
            raise KeyError(f"Checkout {checkout.id} not found")
        self._checkouts[checkout.id] = checkout
