from hypothesis import given
import hypothesis.strategies as st

from blockchain_poc import merkle
from blockchain_poc.utils import sha256_hexdigest
from blockchain_poc.constants import ZERO_HASH

from tests.conftest import st_hashes

SAMPLE_HASH_1 = "0x3e69b2b59951dc2bc46132bd9f801dcf9fe4836b3e6a85cc0c7b5ded4e4c8f18"
SAMPLE_HASH_2 = "0x97a1b62c45656972ff88b07a6865baf725efdf698688a65b3537f3bbc562d715"
SAMPLE_HASH_3 = "0xdb52a8d157ebe2b3330c024d796a40bf12a7727c6ca0a792cbca50dedfb521a2"
SAMPLE_HASH_4 = "0xfcab58021a4ba8ae2dfee76f53ab6d12fe89e8ad36967798622ecabcb24a84df"
HASHES = [SAMPLE_HASH_1, SAMPLE_HASH_2, SAMPLE_HASH_3, SAMPLE_HASH_4]


def test_generate_root_one_level():
    expected = sha256_hexdigest(SAMPLE_HASH_1 + SAMPLE_HASH_2)
    assert merkle.generate_root([SAMPLE_HASH_1, SAMPLE_HASH_2]) == expected
    assert merkle.generate_root([SAMPLE_HASH_2, SAMPLE_HASH_1]) == expected

    expected = sha256_hexdigest(SAMPLE_HASH_1 + SAMPLE_HASH_3)
    assert merkle.generate_root([SAMPLE_HASH_1, SAMPLE_HASH_3]) == expected
    assert merkle.generate_root([SAMPLE_HASH_3, SAMPLE_HASH_1]) == expected


def test_generate_root_multiple_levels():
    h1h2 = sha256_hexdigest(SAMPLE_HASH_1 + SAMPLE_HASH_2)
    h3h4 = sha256_hexdigest(SAMPLE_HASH_3 + SAMPLE_HASH_4)
    expected = sha256_hexdigest(h1h2 + h3h4 if h1h2 < h3h4 else h3h4 + h1h2)
    assert merkle.generate_root(HASHES) == expected


def test_generate_root_odd_leaves():
    h1h2 = sha256_hexdigest(SAMPLE_HASH_1 + SAMPLE_HASH_2)
    h30h = sha256_hexdigest(ZERO_HASH + SAMPLE_HASH_3)
    expected = sha256_hexdigest(h1h2 + h30h if h1h2 < h30h else h30h + h1h2)
    hashes = [SAMPLE_HASH_1, SAMPLE_HASH_2, SAMPLE_HASH_3]
    assert merkle.generate_root(hashes) == expected


def test_generate_proof():
    proof = merkle.generate_proof(SAMPLE_HASH_3, HASHES)
    assert len(proof) == 2
    assert proof[0] == SAMPLE_HASH_4
    assert proof[1] == sha256_hexdigest(SAMPLE_HASH_1 + SAMPLE_HASH_2)


def test_verify_proof_valid():
    root = merkle.generate_root(HASHES)
    proof = merkle.generate_proof(SAMPLE_HASH_3, HASHES)
    assert merkle.verify_proof(SAMPLE_HASH_3, root, proof)


def test_verify_proof_invalid_root():
    proof = merkle.generate_proof(SAMPLE_HASH_3, HASHES)
    assert not merkle.verify_proof(SAMPLE_HASH_3, SAMPLE_HASH_4, proof)


def test_verify_proof_invalid():
    root = merkle.generate_root(HASHES)
    proof = merkle.generate_proof(SAMPLE_HASH_3, HASHES)
    proof[1] = SAMPLE_HASH_2
    assert not merkle.verify_proof(SAMPLE_HASH_3, root, proof)


@st.composite
def hashes_with_target(draw):
    hashes = draw(st.lists(st_hashes, min_size=2, max_size=10_000, unique=True))
    target = draw(st.sampled_from(hashes))
    return (hashes, target)


@given(data=hashes_with_target())
def test_generate_verify_proof(data):
    hashes, target = data
    root = merkle.generate_root(hashes)
    proof = merkle.generate_proof(target, hashes)
    assert merkle.verify_proof(target, root, proof)
