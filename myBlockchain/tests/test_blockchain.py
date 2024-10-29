import gzip
import json
from os import path

from blockchain_poc.blockchain import Blockchain
from blockchain_poc.block import Block
from blockchain_poc.block_header import BlockHeader
from tests.conftest import DATA_DIR

STATE_FILE = path.join(DATA_DIR, "sample", "blockchain.json.gz")


def test_load_state():
    blockchain = Blockchain(max_txs_per_block=5)
    blockchain.load_state(STATE_FILE)
    with gzip.open(STATE_FILE) as f:
        assert blockchain.height + 1 == len(json.load(f))


def test_prove_inclusion():
    blockchain = Blockchain.from_file(STATE_FILE, max_txs_per_block=5)
    tx_hash = "0xc06eaef0a51caea2e6fcf8ffbc38a0b3c6cf39a8a8214501082a30c265c120ac"  # 3rd tx in block 3
    proof = blockchain.generate_inclusion_proof(3, tx_hash)
    assert blockchain.verify_inclusion_proof(3, tx_hash, proof)


def test_get_next_difficulty():
    blockchain = Blockchain()
    block = Block(
        header=BlockHeader(
            difficulty=0,
            hash="",
            previous_block_header_hash="",
            timestamp=0,
            height=0,
            miner="",
            nonce=0,
            transactions_count=0,
            transactions_merkle_root="",
        ),
        transactions=[],
    )
    blockchain.blocks.append(block)

    block.header.height = 1
    assert blockchain.get_next_difficulty() == 1
    block.header.height = 48
    assert blockchain.get_next_difficulty() == 1
    block.header.height = 49
    assert blockchain.get_next_difficulty() == 2
    block.header.height = 98
    assert blockchain.get_next_difficulty() == 2
    block.header.height = 99
    assert blockchain.get_next_difficulty() == 3
