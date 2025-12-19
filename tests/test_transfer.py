from datetime import datetime, timedelta
from uuid import UUID

import pytest

from equipment_ellie.actions import ActiveCheckoutNotFoundError, transfer_checkout
from equipment_ellie.models import Checkout
from equipment_ellie.store import CheckoutStore


def test_transfer_checkout_closes_active_and_creates_new_checkout() -> None:
    store = CheckoutStore()
    equipment_id = UUID("00000000-0000-0000-0000-000000000001")
    old_person_id = UUID("00000000-0000-0000-0000-000000000010")
    new_person_id = UUID("00000000-0000-0000-0000-000000000020")
    now = datetime(2024, 1, 1, 8, 30, 0)

    store.add(
        Checkout(
            id=UUID("00000000-0000-0000-0000-000000000100"),
            equipment_id=equipment_id,
            person_id=old_person_id,
            checked_out_at=now - timedelta(days=1),
            due_at=now,
        )
    )

    records = list(
        transfer_checkout(
            store=store,
            equipment_id=equipment_id,
            new_person_id=new_person_id,
            now=now,
        )
    )

    assert len(records) == 2
    closed_checkout = next(record for record in records if record.person_id == old_person_id)
    new_checkout = next(record for record in records if record.person_id == new_person_id)

    assert closed_checkout.checked_in_at == now
    assert closed_checkout.transferred_at == now
    assert closed_checkout.transferred_to_person_id == new_person_id

    assert new_checkout.checked_out_at == now
    assert new_checkout.due_at == now + timedelta(days=1)


def test_transfer_requires_active_checkout() -> None:
    store = CheckoutStore()
    equipment_id = UUID("00000000-0000-0000-0000-000000000002")
    new_person_id = UUID("00000000-0000-0000-0000-000000000030")

    with pytest.raises(ActiveCheckoutNotFoundError):
        transfer_checkout(
            store=store,
            equipment_id=equipment_id,
            new_person_id=new_person_id,
        )
