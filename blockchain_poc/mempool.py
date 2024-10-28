from __future__ import annotations

import json
from typing import Iterable

from .transaction import Transaction
from .utils import open_file


class Mempool:
    def __init__(self, transactions: Iterable[Transaction]):
        self.transactions = set(transactions)

    def get_live_transactions(self, timestamp: int):
        return [tx for tx in self.transactions if tx.lock_time <= timestamp]

    def remove_transactions(self, transactions: Iterable[Transaction]):
        self.transactions -= set(transactions)

    @classmethod
    def from_file(cls, filename: str) -> Mempool:
        with open_file(filename) as f:
            return cls(set(Transaction.from_dict(t) for t in json.load(f)))

    def to_file(self, filename: str):
        with open_file(filename, "wt") as f:
            json.dump([t.to_dict() for t in self.transactions], f)
