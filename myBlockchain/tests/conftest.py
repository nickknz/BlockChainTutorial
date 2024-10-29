from os import path

import hypothesis.strategies as st

from blockchain_poc.constants import DECIMAL_MULTIPLIER
from blockchain_poc.utils import int_to_hash

DATA_DIR = path.join(path.dirname(path.abspath(__file__)), "data")

st_hashes = st.integers(min_value=0, max_value=2**256 - 1).map(int_to_hash)
st_addresses = st.integers(min_value=0, max_value=2**160 - 1).map(int_to_hash)


def st_monetary_amounts(max_amount: int = 1_000_000_000):
    return st.integers(min_value=0, max_value=max_amount).map(
        lambda x: x * DECIMAL_MULTIPLIER
    )
