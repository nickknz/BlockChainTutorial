from typing import List

from .transaction import Transaction
from .blockchain import Blockchain
from .block import Block
from .mempool import Mempool


class Miner:
    def __init__(self, address: str, blockchain: Blockchain, mempool: Mempool):
        self.address = address
        self.blockchain = blockchain
        self.mempool = mempool

    def mine_next(self):
        timestamp = self.blockchain.timestamp + 10
        # choose the most profitable transactions
        txs_to_mine = self.get_most_profitable_transactions(timestamp)
        block = Block.mine(
            difficulty=self.blockchain.get_next_difficulty(),
            height=self.blockchain.height + 1,
            miner=self.address,
            previous_block_header_hash=self.blockchain.head.header.hash,
            timestamp=timestamp,
            transactions=txs_to_mine,
        )
        self.blockchain.process_block(block)
        self.mempool.remove_transactions(txs_to_mine)
        return block

    def get_most_profitable_transactions(self, timestamp: int) -> List[Transaction]:
        txs_by_fee = sorted(
            self.mempool.get_live_transactions(timestamp),
            key=lambda tx: tx.transaction_fee,
            reverse=True,
        )

        balances = self.blockchain.balances.copy()
        txs_to_mine = []
        for tx in txs_by_fee:
            if balances.get(tx.sender, 0) >= tx.amount + tx.transaction_fee:
                Blockchain.update_balances(balances, tx, self.address)
                txs_to_mine.append(tx)
                if len(txs_to_mine) == self.blockchain.max_txs_per_block:
                    break
        return txs_to_mine
