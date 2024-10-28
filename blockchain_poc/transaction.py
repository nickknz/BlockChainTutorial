from __future__ import annotations
import hashlib

from dataclasses import asdict, dataclass
from typing import cast
from ecdsa import SigningKey, VerifyingKey
from ecdsa.util import sigdecode_der, sigencode_der

from .utils import SHA256Hashable, from_hex, to_hex


@dataclass
class Transaction(SHA256Hashable):
    sender: str
    receiver: str
    amount: int
    transaction_fee: int
    lock_time: int
    signature: str = ""

    @classmethod
    def from_dict(cls, obj: dict) -> Transaction:
        return cls(**obj)

    def to_dict(self) -> dict:
        return asdict(self)

    def compute_hash_to_sign(self):
        string_to_sign = self.serialize(fields_to_exclude=["signature"]).encode()
        return hashlib.sha256(string_to_sign).digest()

    def sign(self, private_key: SigningKey):
        hash_to_sign = self.compute_hash_to_sign()
        signature = private_key.sign_digest(hash_to_sign, sigencode=sigencode_der)
        public_key = cast(VerifyingKey, private_key.verifying_key)
        encoded_public_key = to_hex(public_key.to_der())
        full_signature = encoded_public_key + "," + to_hex(signature)
        self.signature = full_signature

    def verify_signature(self) -> bool:
        encoded_public_key, signature = self.signature.split(",")
        public_key = VerifyingKey.from_der(from_hex(encoded_public_key))
        return public_key.verify_digest(
            from_hex(signature),
            self.compute_hash_to_sign(),
            sigdecode=sigdecode_der,  # type: ignore
        )

    def __hash__(self):
        digest = hashlib.sha256(self.serialize().encode()).digest()
        return int.from_bytes(digest, "big")
