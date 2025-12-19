from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable
from uuid import UUID, uuid4

from equipment_ellie.models import Checkout
from equipment_ellie.store import CheckoutStore


class ActiveCheckoutNotFoundError(RuntimeError):
    pass


def transfer_checkout(
    *,
    store: CheckoutStore,
    equipment_id: UUID,
    new_person_id: UUID,
    now: datetime | None = None,
) -> Iterable[Checkout]:
    """Transfer an active checkout to a new person.

    Returns the updated (closed) checkout and the newly created checkout.
    """
    timestamp = now or datetime.utcnow()
    active_checkout = store.active_for_equipment(equipment_id)
    if active_checkout is None:
        raise ActiveCheckoutNotFoundError(
            f"No active checkout found for equipment {equipment_id}."
        )

    store.close_checkout(
        active_checkout,
        checked_in_at=timestamp,
        transferred_to_person_id=new_person_id,
    )

    new_checkout = Checkout(
        id=uuid4(),
        equipment_id=equipment_id,
        person_id=new_person_id,
        checked_out_at=timestamp,
        due_at=timestamp + timedelta(days=1),
    )
    store.add(new_checkout)
    return store.list_for_equipment(equipment_id)
