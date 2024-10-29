import json
from os import path

from blockchain_poc.block_header import BlockHeader
from tests.conftest import DATA_DIR


def test_sample():
    with open(path.join(DATA_DIR, "sample-header.json")) as f:
        header = BlockHeader(**json.load(f))
    expected = "0x852e08629d3f624833a523e3b4bbdde45f87a44e7a5c2574eefe28528373cdbf"
    assert header.sha256_hash() == expected


def test_hash():
    with open(path.join(DATA_DIR, "header-119.json")) as f:
        header = BlockHeader(**json.load(f))
    assert header.sha256_hash() == header.hash


def test_previous_hash():
    with open(path.join(DATA_DIR, "header-119.json")) as f:
        header_119 = BlockHeader(**json.load(f))
    with open(path.join(DATA_DIR, "header-120.json")) as f:
        header_120 = BlockHeader(**json.load(f))
    assert (
        header_120.previous_block_header_hash
        == header_119.sha256_hash()
        == header_119.hash
    )


def test_is_below_target():
    with open(path.join(DATA_DIR, "header-119.json")) as f:
        header = BlockHeader(**json.load(f))
    assert header.is_below_target()
