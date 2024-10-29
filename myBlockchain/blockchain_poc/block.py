from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import List, Optional

from . import merkle
from .block_header import BlockHeader
from .constants import ZERO_HASH
from .transaction import Transaction


@dataclass
class Block:
    header: BlockHeader
    transactions: List[Transaction]

    @classmethod
    def from_dict(cls, obj) -> Block:
        return Block(
            header=BlockHeader(**obj["header"]),
            transactions=[Transaction.from_dict(t) for t in obj["transactions"]],
        )

    def to_dict(self) -> dict:
        return {
            "header": asdict(self.header),
            "transactions": [t.to_dict() for t in self.transactions],
        }

    @staticmethod
    def _compute_transactions_merkle_root(transactions: List[Transaction]) -> str:
        transaction_hashes = [t.sha256_hash() for t in transactions]
        return merkle.generate_root(transaction_hashes)

    def compute_transactions_merkle_root(self):
        return self._compute_transactions_merkle_root(self.transactions)

    @classmethod
    def mine(
        cls,
        difficulty: int,
        height: int,
        miner: str,
        previous_block_header_hash: str,
        timestamp: int,
        transactions: List[Transaction],
    ) -> Block:
        header = BlockHeader(
            difficulty=difficulty,
            height=height,
            miner=miner,
            previous_block_header_hash=previous_block_header_hash,
            timestamp=timestamp,
            nonce=0,
            transactions_count=len(transactions),
            transactions_merkle_root=cls._compute_transactions_merkle_root(
                transactions
            ),
        )
        while not header.is_below_target():
            header.nonce += 1
        header.hash = header.sha256_hash()

        return cls(header=header, transactions=transactions)

    def validate(self, max_txs_per_block: int, head: Optional[Block] = None):
        if (
            self.header.transactions_merkle_root
            != self.compute_transactions_merkle_root()
        ):
            raise ValueError("invalid transactions_merkle_root")

        if len(self.transactions) > max_txs_per_block:
            raise ValueError("too many transactions")

        if self.header.transactions_count != len(self.transactions):
            raise ValueError("invalid transactions_count")

        if head is None:
            if self.header.previous_block_header_hash != ZERO_HASH:
                raise ValueError("invalid previous_block_header_hash")
            return

        if self.header.height != head.header.height + 1:
            raise ValueError("invalid height")

        if self.header.previous_block_header_hash != head.header.hash:
            raise ValueError("invalid previous_block_header_hash")

        if self.header.timestamp <= head.header.timestamp:
            raise ValueError("invalid timestamp")
