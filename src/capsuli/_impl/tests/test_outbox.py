from copy import copy
import pytest
from typing_extensions import Buffer
from capsuli._impl.outbox import Outbox


@pytest.fixture
def outbox() -> Outbox:
    return Outbox()


@pytest.fixture
def message() -> Buffer:
    return b"abcd"


def test_create_outbox() -> None:
    box = Outbox()
    assert box._queue.qsize() == 0


def test_deposit_message(outbox: Outbox, message: Buffer) -> None:
    outbox.deposit(message)
    assert outbox._queue.qsize() == 1
    assert outbox._queue.get() == message


def test_retrieve_message(outbox: Outbox, message: Buffer) -> None:
    outbox._queue.put(message)
    assert outbox.retrieve() == message


def test_deposit_retrieve_order(outbox: Outbox, message: Buffer) -> None:
    m1 = copy(message)
    m2 = copy(message)

    outbox.deposit(m1)
    outbox.deposit(m2)

    assert outbox.retrieve() == m1
    assert outbox.retrieve() == m2
