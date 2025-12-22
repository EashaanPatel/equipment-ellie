"""Checkout and check-in services."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

from .models import Checkout, Equipment, EquipmentStatus
from .repository import CheckoutRepository


def checkout_equipment(equipment: Equipment, repository: CheckoutRepository) -> Checkout:
    """Checkout equipment, creating a new checkout record.

    Raises:
        ValueError: If the equipment is not available for checkout.
    """

    if equipment.status != EquipmentStatus.AVAILABLE:
        raise ValueError("Equipment is not available for checkout")

    checked_out_at = datetime.now(timezone.utc)
    due_at = checked_out_at + timedelta(hours=24)
    checkout = Checkout(
        id=0,
        equipment_id=equipment.id,
        checked_out_at=checked_out_at,
        due_at=due_at,
    )
    created_checkout = repository.create(checkout)
    equipment.status = EquipmentStatus.CHECKED_OUT
    return created_checkout


def checkin_equipment(equipment: Equipment, repository: CheckoutRepository) -> Checkout:
    """Check in equipment, closing the active checkout record.

    Raises:
        ValueError: If there is no active checkout to close.
    """

    active_checkout = repository.get_active_for_equipment(equipment.id)
    if active_checkout is None:
        raise ValueError("No active checkout to check in")

    checked_in_at = datetime.now(timezone.utc)
    updated_checkout = replace(active_checkout, checked_in_at=checked_in_at)
    repository.update(updated_checkout)
    equipment.status = EquipmentStatus.AVAILABLE
    return updated_checkout
