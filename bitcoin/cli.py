import argparse
import json

from .block import Block
from .transaction import Transaction
from .blockchain import Blockchain
from .mempool import Mempool
from .miner import Miner
from . import transaction_generator
from .utils import open_file

parser = argparse.ArgumentParser(
    prog="blockchain_poc", description="Proof of Concept blockchain implementation"
)
parser.add_argument(
    "--blockchain-state", required=True, help="Path to blockchain state file"
)

subparsers = parser.add_subparsers(dest="command", help="Command to run")

produce_blocks_parser = subparsers.add_parser("produce-blocks", help="Produce blocks")
produce_blocks_parser.add_argument(
    "--mempool", required=True, help="Path to mempool file"
)
produce_blocks_parser.add_argument(
    "-n", "--number", type=int, default=1, help="Number of blocks to produce"
)
produce_blocks_parser.add_argument(
    "--blockchain-output", required=True, help="Path to blockchain output file"
)
produce_blocks_parser.add_argument(
    "--mempool-output", required=True, help="Path to mempool output file"
)
produce_blocks_parser.add_argument(
    "--miner-address",
    default="0x0000ee1509c22458e88d9c0fedd9fbbf4a18994c",
    help="Address of the miner",
)


transaction_hash_parser = subparsers.add_parser(
    "get-tx-hash", help="Retrieves the hash of a transaction"
)
transaction_hash_parser.add_argument("block", type=int, help="Block number")
transaction_hash_parser.add_argument(
    "index", type=int, help="Index of the transaction in the block"
)

generate_proof_parser = subparsers.add_parser(
    "generate-proof", help="Generate an inclusion proof for a transaction"
)
generate_proof_parser.add_argument("block", type=int, help="Block number")
generate_proof_parser.add_argument(
    "hash", help="Hash of thee transaction for which to produce the proof"
)
generate_proof_parser.add_argument(
    "-o", "--output", help="Output file for the proof (default: stdout)"
)

verify_proof_parser = subparsers.add_parser(
    "verify-proof", help="Verify an inclusion proof for a transaction"
)
verify_proof_parser.add_argument("proof", help="File containig the JSON proof")

generate_transactions_parser = subparsers.add_parser(
    "generate-txs", help="Generate transactions"
)
generate_transactions_parser.add_argument(
    "-n",
    "--number",
    type=int,
    default=100,
    help="The number of transactions to generate",
)
generate_transactions_parser.add_argument(
    "-a", "--accounts", required=True, help="File containing the accounts"
)
generate_transactions_parser.add_argument(
    "-o", "--output", required=True, help="Output file for the transactions"
)


def produce_blocks(args):
    blockchain = Blockchain.from_file(args.blockchain_state)
    mempool = Mempool.from_file(args.mempool)
    miner = Miner(args.miner_address, blockchain, mempool)
    for _ in range(args.number):
        miner.mine_next()
    blockchain.write_state(args.blockchain_output)
    mempool.to_file(args.mempool_output)


def get_transaction_hash(args):
    blockchain = Blockchain.from_file(args.blockchain_state)
    block: Block = blockchain.blocks[args.block]
    tx: Transaction = block.transactions[args.index]
    print(tx.sha256_hash())


def generate_proof(args):
    blockchain = Blockchain.from_file(args.blockchain_state)
    proof = blockchain.generate_inclusion_proof(args.block, args.hash)
    full_proof = {
        "block": args.block,
        "hash": args.hash,
        "proof": proof,
    }
    if args.output:
        with open(args.output, "w") as f:
            json.dump(full_proof, f)
    else:
        print(json.dumps(full_proof, indent=2))


def verify_proof(args):
    blockchain = Blockchain.from_file(args.blockchain_state)
    with open(args.proof) as f:
        proof = json.load(f)
    if blockchain.verify_inclusion_proof(proof["block"], proof["hash"], proof["proof"]):
        print("proof valid")
    else:
        print("proof invalid")


def generate_transactions(args):
    blockchain = Blockchain.from_file(args.blockchain_state)
    accounts = transaction_generator.load_accounts(args.accounts)
    txs = transaction_generator.generate_transactions(blockchain, accounts, args.number)
    with open_file(args.output, "wt") as f:
        json.dump([t.to_dict() for t in txs], f)


def main():
    args = parser.parse_args()
    if args.command == "produce-blocks":
        produce_blocks(args)
    elif args.command == "get-tx-hash":
        get_transaction_hash(args)
    elif args.command == "generate-proof":
        generate_proof(args)
    elif args.command == "verify-proof":
        verify_proof(args)
    elif args.command == "generate-txs":
        generate_transactions(args)
    else:
        parser.error("no command specified")
