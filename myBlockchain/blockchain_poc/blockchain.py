from __future__ import annotations
import json
from typing import Dict, List, Optional

from . import merkle
from .block import Block
from .constants import ZERO_ADDRESS
from .transaction import Transaction
from .utils import open_file


class Blockchain:
    def __init__(self, max_txs_per_block: int = 100):
        self.blocks: List[Block] = []
        self.max_txs_per_block = max_txs_per_block
        self.balances = {}

    @classmethod
    def from_file(cls, filename: str, max_txs_per_block: int = 100) -> Blockchain:
        blockchain = cls(max_txs_per_block)
        blockchain.load_state(filename)
        return blockchain

    def load_state(self, state_path: str):
        with open_file(state_path, "r") as f:
            state = json.load(f)
        for block in state:
            self.process_block(Block.from_dict(block))

    def write_state(self, state_path: str):
        blocks = [b.to_dict() for b in self.blocks]
        with open_file(state_path, "wt") as f:
            json.dump(blocks, f)

    def process_block(self, block: Block):
        head = self.head if len(self.blocks) > 0 else None
        block.validate(self.max_txs_per_block, head=head)
        for tx in block.transactions:
            self.process_transaction(block.header.miner, block.header.height, tx)
        self.blocks.append(block)

    def process_transaction(self, miner: str, height: int, transaction: Transaction):
        if height > 0:
            to_debit = transaction.amount + transaction.transaction_fee
            if self.balances[transaction.sender] < to_debit:
                raise ValueError(
                    f"insufficient funds for {transaction.sender}: {self.balances[transaction.sender]} < {to_debit}"
                )
        else:
            if transaction.sender != ZERO_ADDRESS:
                raise ValueError("invalid sender")
        self.update_balances(self.balances, transaction, miner)

    @staticmethod
    def update_balances(
        balances: Dict[str, int], tx: Transaction, miner: Optional[str] = None
    ):
        if tx.sender != ZERO_ADDRESS:
            balances[tx.sender] -= tx.amount + tx.transaction_fee
        if miner:
            balances[miner] = tx.transaction_fee + balances.get(miner, 0)
        balances[tx.receiver] = tx.amount + balances.get(tx.receiver, 0)

    def generate_inclusion_proof(
        self, block_height: int, transaction_hash: str
    ) -> List[str]:
        block = self.blocks[block_height]
        return merkle.generate_proof(
            transaction_hash, [t.sha256_hash() for t in block.transactions]
        )

    def get_next_difficulty(self):
        difficulty = 1 + (self.height + 1) // 50
        if difficulty > 6:
            return 6
        return difficulty

    def verify_inclusion_proof(
        self, block_height: int, transaction_hash: str, proof: List[str]
    ) -> bool:
        merkle_root = self.blocks[block_height].header.transactions_merkle_root
        return merkle.verify_proof(transaction_hash, merkle_root, proof)

    @property
    def height(self) -> int:
        return self.head.header.height

    @property
    def timestamp(self) -> int:
        return self.head.header.timestamp

    @property
    def head(self) -> Block:
        if len(self.blocks) == 0:
            raise ValueError("chain is not initialized")
        return self.blocks[-1]
