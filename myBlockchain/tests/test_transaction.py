import json
from os import path

import hypothesis.strategies as st
from ecdsa import SigningKey, curves
from hypothesis import given

from blockchain_poc.transaction import Transaction
from tests.conftest import DATA_DIR, st_addresses, st_monetary_amounts


@st.composite
def st_transactions(draw):
    return Transaction(
        sender=draw(st_addresses),
        receiver=draw(st_addresses),
        amount=draw(st_monetary_amounts()),
        transaction_fee=draw(st_monetary_amounts(max_amount=100)),
        lock_time=draw(st.integers(min_value=0, max_value=3600)),
    )


def test_compute_hash():
    transaction = Transaction(
        amount=100,
        transaction_fee=5,
        lock_time=1674523800,
        sender="0x1cf330a1b7cf34ddefb72553980ac782a8dda222",
        receiver="0x4e7d61B150BC9e96E7BE7e45CD6e82b064E679F9",
        signature="0x3059301306072a8648ce3d020106082a8648ce3d030107034200041e1b19692c75eee88906c057c26106867d6460dbae929891a0d8111d616716b95b2a1e6cacf2029781426c8e70c02e1166778e2f8181fb042f3094a5590b58a0,0x3044022077889f0de27f45a0e84316a9f8414a69b84053b1b134d25d68ccaff4e4c7a37a022062216be5a99d2adca36f0b577c8527d677a4d5d7a32172b27520747b753c0c29",
    )
    assert transaction.verify_signature()
    assert (
        transaction.sha256_hash()
        == "0x61ad3c6bb8974ea49a2202f05cc2de24afd0f5b8434ea0051293856667ec4261"
    )


def test_serialization():
    with open(path.join(DATA_DIR, "mempool-transaction-1.json")) as f:
        obj = json.load(f)
    transaction = Transaction.from_dict(obj)
    assert transaction.to_dict() == obj


def test_verify_existing_transaction():
    with open(path.join(DATA_DIR, "mempool-transaction-1.json")) as f:
        transaction = Transaction.from_dict(json.load(f))
    assert transaction.verify_signature()


@given(transaction=st_transactions())
def test_sign_and_verify(transaction: Transaction):
    private_key = SigningKey.generate(curve=curves.NIST256p)
    transaction.sign(private_key)
    assert transaction.verify_signature()
