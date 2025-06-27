"""
Core Post-Quantum Cryptography Models and Interfaces
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from pydantic import Field, validator
from datetime import datetime

from dslmodel import DSLModel

class PQCAlgorithmType(str, Enum):
    """NIST-approved PQC algorithm types"""
    # Key Encapsulation Mechanisms (KEM)
    KYBER = "kyber"
    
    # Digital Signatures
    DILITHIUM = "dilithium"
    FALCON = "falcon"
    SPHINCS_PLUS = "sphincs_plus"

class PQCSecurityLevel(int, Enum):
    """NIST security levels for PQC"""
    LEVEL_1 = 1  # Equivalent to AES-128
    LEVEL_2 = 2  # Equivalent to SHA-256/SHA3-256
    LEVEL_3 = 3  # Equivalent to AES-192
    LEVEL_4 = 4  # Equivalent to SHA-384/SHA3-384  
    LEVEL_5 = 5  # Equivalent to AES-256

class PQCKeyPair(DSLModel):
    """Post-quantum cryptographic key pair"""
    algorithm: PQCAlgorithmType = Field(..., description="PQC algorithm type")
    security_level: PQCSecurityLevel = Field(..., description="NIST security level")
    public_key: bytes = Field(..., description="Public key bytes")
    private_key: Optional[bytes] = Field(None, description="Private key bytes (None if public only)")
    key_id: str = Field(..., description="Unique key identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Key expiration time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('expires_at')
    def validate_expiration(cls, v, values):
        if v and 'created_at' in values:
            if v <= values['created_at']:
                raise ValueError("Expiration must be after creation time")
        return v
    
    def is_expired(self) -> bool:
        """Check if key has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

class PQCSignature(DSLModel):
    """Post-quantum digital signature"""
    algorithm: PQCAlgorithmType = Field(..., description="Signature algorithm")
    signature: bytes = Field(..., description="Signature bytes")
    message_hash: str = Field(..., description="Hash of signed message")
    key_id: str = Field(..., description="ID of signing key")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PQCCiphertext(DSLModel):
    """Post-quantum encrypted data"""
    algorithm: PQCAlgorithmType = Field(..., description="Encryption algorithm")
    ciphertext: bytes = Field(..., description="Encrypted data")
    encapsulated_key: Optional[bytes] = Field(None, description="KEM encapsulated key")
    recipient_key_id: str = Field(..., description="Recipient's key ID")
    sender_key_id: Optional[str] = Field(None, description="Sender's key ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PQCProvider(ABC):
    """Abstract base class for PQC algorithm providers"""
    
    @abstractmethod
    def generate_keypair(self, security_level: PQCSecurityLevel) -> PQCKeyPair:
        """Generate a new PQC key pair"""
        pass
    
    @abstractmethod
    def sign(self, message: bytes, private_key: bytes) -> PQCSignature:
        """Create a PQC signature"""
        pass
    
    @abstractmethod
    def verify(self, message: bytes, signature: PQCSignature, public_key: bytes) -> bool:
        """Verify a PQC signature"""
        pass
    
    @abstractmethod
    def encrypt(self, plaintext: bytes, public_key: bytes) -> PQCCiphertext:
        """Encrypt data using PQC"""
        pass
    
    @abstractmethod
    def decrypt(self, ciphertext: PQCCiphertext, private_key: bytes) -> bytes:
        """Decrypt PQC ciphertext"""
        pass

class HybridPQCScheme(DSLModel):
    """Hybrid classical + post-quantum scheme for transition period"""
    classical_algorithm: str = Field(..., description="Classical algorithm (e.g., RSA, ECDSA)")
    pqc_algorithm: PQCAlgorithmType = Field(..., description="PQC algorithm")
    mode: str = Field("concatenate", description="Combination mode: concatenate, nested, or xor")
    transition_date: datetime = Field(..., description="Date to fully transition to PQC")
    
    def should_use_hybrid(self) -> bool:
        """Check if still in hybrid mode"""
        return datetime.utcnow() < self.transition_date