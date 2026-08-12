"""Core models and interfaces for post-quantum cryptographic operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PQCError(RuntimeError):
    """Base error for cryptographic capability failures."""


class PQCBackendUnavailable(PQCError):
    """Raised when the optional production cryptography backend is unavailable."""


class PQCUnsupportedAlgorithm(PQCError):
    """Raised when a historical algorithm has no admitted production backend."""


class PQCOperationError(PQCError):
    """Raised when a cryptographic operation fails authentication or admission."""


class PQCAlgorithmType(str, Enum):
    """Canonical production algorithms plus compatibility aliases."""

    ML_KEM = "ml_kem"
    ML_DSA = "ml_dsa"
    KYBER = "ml_kem"
    DILITHIUM = "ml_dsa"
    FALCON = "falcon"
    SPHINCS_PLUS = "sphincs_plus"


class PQCSecurityLevel(int, Enum):
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class _PQCModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")


class PQCKeyPair(_PQCModel):
    """Serialized public/private material produced by an admitted provider."""

    algorithm: PQCAlgorithmType
    security_level: PQCSecurityLevel
    public_key: bytes
    private_key: bytes | None = None
    key_id: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=_utcnow)
    expires_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("expires_at")
    @classmethod
    def validate_expiration(cls, value: datetime | None, info: Any) -> datetime | None:
        created_at = info.data.get("created_at")
        if value is not None and created_at is not None and value <= created_at:
            raise ValueError("expiration must be after creation time")
        return value

    def is_expired(self) -> bool:
        return self.expires_at is not None and _utcnow() > self.expires_at


class PQCSignature(_PQCModel):
    """Signature bytes plus replay metadata; verification never trusts metadata alone."""

    algorithm: PQCAlgorithmType
    signature: bytes = Field(..., min_length=1)
    message_hash: str = Field(..., min_length=1)
    key_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=_utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PQCCiphertext(_PQCModel):
    """Authenticated payload ciphertext plus KEM encapsulation material."""

    algorithm: PQCAlgorithmType
    ciphertext: bytes = Field(..., min_length=1)
    encapsulated_key: bytes | None = None
    recipient_key_id: str = Field(..., min_length=1)
    sender_key_id: str | None = None
    timestamp: datetime = Field(default_factory=_utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PQCProvider(ABC):
    """Execution contract for one cryptographic backend."""

    @abstractmethod
    def generate_keypair(self, security_level: PQCSecurityLevel) -> PQCKeyPair:
        """Generate and serialize a provider key pair."""

    @abstractmethod
    def sign(self, message: bytes, private_key: bytes) -> PQCSignature:
        """Cryptographically sign a message."""

    @abstractmethod
    def verify(self, message: bytes, signature: PQCSignature, public_key: bytes) -> bool:
        """Cryptographically verify a signature against public key bytes."""

    @abstractmethod
    def encrypt(self, plaintext: bytes, public_key: bytes) -> PQCCiphertext:
        """KEM-encapsulate a shared key and AEAD-encrypt a payload."""

    @abstractmethod
    def decrypt(self, ciphertext: PQCCiphertext, private_key: bytes) -> bytes:
        """Decapsulate and authenticate/decrypt a payload."""


class HybridPQCScheme(_PQCModel):
    """Configuration record for callers that implement an external hybrid scheme."""

    classical_algorithm: str = Field(..., min_length=1)
    pqc_algorithm: PQCAlgorithmType
    mode: str = Field("concatenate", pattern="^(concatenate|nested|xor)$")
    transition_date: datetime

    def should_use_hybrid(self) -> bool:
        transition = self.transition_date
        if transition.tzinfo is None:
            transition = transition.replace(tzinfo=timezone.utc)
        return _utcnow() < transition
