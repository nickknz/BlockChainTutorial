from typing import Generator, List

from .constants import ZERO_HASH
from .utils import hash_pair


def _compute_next_hashes(hashes: List[str]) -> List[str]:
    return [hash_pair(a, b) for a, b in zip(hashes[::2], hashes[1::2])]


def _iterate_merkle_tree(hashes: List[str]) -> Generator[List[str], None, None]:
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(ZERO_HASH)
        yield hashes
        hashes = _compute_next_hashes(hashes)


def generate_root(hashes: List[str]) -> str:
    return hash_pair(*list(_iterate_merkle_tree(hashes))[-1])


def generate_proof(target: str, hashes: List[str]) -> List[str]:
    proof = []
    target_index = hashes.index(target)
    for hashes in _iterate_merkle_tree(hashes):
        proof_item_index = target_index + (1 if target_index % 2 == 0 else -1)
        proof.append(hashes[proof_item_index])
        target_index //= 2
    return proof


def verify_proof(target: str, root: str, proof: List[str]) -> bool:
    current = target
    for hash_value in proof:
        current = hash_pair(current, hash_value)
    return current == root
