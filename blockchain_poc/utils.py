from contextlib import contextmanager
import dataclasses
import gzip
import hashlib
from io import TextIOWrapper
from typing import BinaryIO, Generator, List, Optional, TextIO, Union, cast


def sha256_hexdigest(data: Union[str, bytes]) -> str:
    if isinstance(data, str):
        data = data.encode()
    hashed = hashlib.sha256(data)
    return "0x" + hashed.hexdigest()


def hash_pair(a: str, b: str) -> str:
    if a < b:
        return sha256_hexdigest(a + b)
    else:
        return sha256_hexdigest(b + a)


def int_to_hash(n: int) -> str:
    return to_hex(n.to_bytes(32, "big"))


def to_hex(value: bytes) -> str:
    return "0x" + value.hex()


def from_hex(value: str) -> bytes:
    return bytes.fromhex(value[2:])


@contextmanager
def open_file(path: str, mode: str = "rb") -> Generator[TextIOWrapper, None, None]:
    open_func = gzip.open if path.endswith(".gz") else open
    with open_func(path, mode) as f:
        yield cast(TextIOWrapper, f)


class Serializable:
    def serialize(self, fields_to_exclude: Optional[List[str]] = None) -> str:
        if fields_to_exclude is None:
            fields_to_exclude = self.fields_to_exclude()
        as_dict = sorted(dataclasses.asdict(self).items(), key=lambda x: x[0])
        values = [f"{v}" for k, v in as_dict if k not in fields_to_exclude]
        return ",".join(values)

    def fields_to_exclude(self):
        return []


class SHA256Hashable(Serializable):
    def sha256_hash(self):
        return sha256_hexdigest(self.serialize())
