from dataclasses import dataclass

from .utils import SHA256Hashable


@dataclass
class BlockHeader(SHA256Hashable):
    difficulty: int
    height: int
    miner: str
    nonce: int
    previous_block_header_hash: str
    timestamp: int
    transactions_count: int
    transactions_merkle_root: str
    hash: str = ""

    def fields_to_exclude(self):
        return ["hash"]

    # return true or false
    def is_below_target(self):
        return self.sha256_hash()[2:].startswith("0" * self.difficulty)
