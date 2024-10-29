# Sample solution for Principles of Distributed Ledgers: Tutorial 1

This repository contains a sample solution for the first tutorial of the course Principles of Distributed Ledgers.
The tutorial is available on the course website.

The solution is written in Python but this tutorial is language-agnostic and can be written in any language.

The code for different parts of the tutorial is in the following files:

* Load state from file: [Blockchain.load_state](./blockchain_poc/blockchain.py#L24)
* Finding a set of executable transactions: [Miner.get_most_profitable_transactions](./blockchain_poc/miner.py#L30) (note that this includes the bonus part)
* Constructing the Merkle tree/root: [merkle.generate_root](./blockchain_poc/merkle.py#L19)
* Creating a new block: [Miner.mine_next](./blockchain_poc/miner.py#L15)
* Proof-of-work algorithm: [Block.mine](./blockchain_poc/block.py#L39)
* Write state to file: [Blockchain.write_state](./blockchain_poc/blockchain.py#L30)
* Produce an inclusion proof: [Blockchain.generate_inclusion_proof](./blockchain_poc/blockchain.py#L64)
* Verify an inclusion proof: [Blockchain.verify_inclusion_proof](./blockchain_poc/blockchain.py#L78)
* Keep track of balances: [Blockchain.process_transaction](./blockchain_poc/blockchain.py#L42)
* Verify signatures: [Transaction.verify_signature](./blockchain_poc/transaction.py#L40)
* Generate new transactions: [transaction_generator.generate_transactions](./blockchain_poc/transaction_generator.py#L21)


## Trying out the code

We recommend using a new virtual environment for this project.
You can create a new virtual environment and activate it with the following command:

```
python3 -m venv venv
source venv/bin/activate
```

The project can then be installed with the following command:

```
pip install -e .
```

If the installation succeeds, the following command should succeed:

```
blockchain-poc --help
```

The CLI tool can be used as follows:

```
# produce 15 blocks, reading the state from ./data/blockchain.json.gz
# the mempool from ./data/mempool.json.gz
# writing the new state to new-blockchain.json.gz and the new mempool to new-mempool.json.gz
blockchain-poc --blockchain-state ./data/blockchain.json.gz produce-blocks --mempool ./data/mempool.json.gz --blockchain-output new-blockchain.json.gz --mempool-output new-mempool.json.gz -n 15

# get the hash of the 7th transaction in block 18
blockchain-poc --blockchain-state ./data/blockchain.json.gz get-tx-hash 18 7

# generate the inclusion proof for the 7th transaction in block 18 (using hash retrieved above)
# and save it to proof.json
blockchain-poc --blockchain-state ./data/blockchain.json.gz generate-proof 18 0x20f9ca5187d9789d983d238f9e80aba6a8fb2cebd0fa775e075fe79c006b6455 -o proof.json

# verify the inclusion proof saved in proof.json
blockchain-poc --blockchain-state ./data/blockchain.json.gz verify-proof proof.json

# generate 2000 new transactions using accounts in data/keys.json.gz and
# save them to new-mempool.json.gz
blockchain-poc --blockchain-state ./data/blockchain.json.gz generate-txs -n 2000 -o new-mempool.json.gz -a data/keys.json.gz
```


## Running the tests

To run the tests, the `dev` dependencies need to be installed:

```
pip install -e .[dev]
```

The tests can then be run with the following command:

```
pytest
```
