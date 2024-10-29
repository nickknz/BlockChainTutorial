import json
import random
from typing import Dict, List

import ecdsa

from .blockchain import Blockchain
from .transaction import Transaction
from .utils import from_hex, open_file


def load_accounts(filename: str) -> Dict[str, ecdsa.SigningKey]:
    with open_file(filename) as f:
        raw_accounts = json.load(f)
    accounts = {}
    for address, private_key in raw_accounts.items():
        accounts[address] = ecdsa.SigningKey.from_der(from_hex(private_key))
    return accounts


def generate_transactions(
    blockchain: Blockchain, accounts: Dict[str, ecdsa.SigningKey], count: int
) -> List[Transaction]:
    transactions = []
    balances = blockchain.balances.copy()
    addresses = list(accounts)
    while len(transactions) < count:
        sender = random.choice(addresses)
        receiver = random.choice(addresses)
        transaction_fee = random.randint(1, 10)
        if transaction_fee >= balances.get(sender, 0):
            continue
        tx = Transaction(
            amount=random.randint(0, balances[sender] - transaction_fee),
            lock_time=blockchain.timestamp + random.randint(0, 3600),
            receiver=receiver,
            sender=sender,
            transaction_fee=transaction_fee,
        )
        tx.sign(accounts[sender])
        transactions.append(tx)
        Blockchain.update_balances(balances, tx)
    return transactions
