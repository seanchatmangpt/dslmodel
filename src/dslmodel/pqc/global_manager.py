"""Policy-driven PQC manager.

This module deliberately does not embed jurisdictional compliance claims or
transition dates. Callers must supply their authoritative regional policies.
Cryptographic operations are delegated only to admitted ML-KEM/ML-DSA
providers; historical algorithm identifiers are never selected for new work.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import Field

from dslmodel import DSLModel
from .algorithms import MLDSAAlgorithm, MLKEMAlgorithm
from .core import (
    PQCAlgorithmType,
    PQCCiphertext,
    PQCKeyPair,
    PQCSignature,
    PQCSecurityLevel,
    PQCUnsupportedAlgorithm,
)


class PQCPolicyRequired(ValueError):
    """Raised when an operation requires authoritative policy not supplied by the caller."""


class PQCRegion(str, Enum):
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    MIDDLE_EAST = "middle_east"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    GLOBAL = "global"


class PQCCompliance(str, Enum):
    """Framework identifiers only; membership does not certify compliance."""

    NIST = "nist"
    ETSI = "etsi"
    ISO = "iso"
    CNSA = "cnsa"
    BSI = "bsi"
    ANSSI = "anssi"
    CCCS = "cccs"


class RegionalPQCPolicy(DSLModel):
    """Caller-supplied policy receipt for one region."""

    region: PQCRegion
    compliance_frameworks: list[PQCCompliance] = Field(default_factory=list)
    allowed_algorithms: list[PQCAlgorithmType]
    minimum_security_level: PQCSecurityLevel
    hybrid_required_until: datetime | None = None
    mandatory_from: datetime | None = None
    additional_requirements: dict[str, Any] = Field(default_factory=dict)
    authority: str = Field(..., min_length=1, description="Policy source/authority identifier")
    observed_at: datetime = Field(..., description="When this policy was observed")


class GlobalPQCConfiguration(DSLModel):
    default_kem_algorithm: PQCAlgorithmType = PQCAlgorithmType.ML_KEM
    default_signature_algorithm: PQCAlgorithmType = PQCAlgorithmType.ML_DSA
    default_security_level: PQCSecurityLevel = PQCSecurityLevel.LEVEL_3
    regional_policies: list[RegionalPQCPolicy] = Field(default_factory=list)
    allow_algorithm_negotiation: bool = True
    require_forward_secrecy: bool = True


class PQCKeyStore(DSLModel):
    store_id: str
    region: PQCRegion
    keys: dict[str, PQCKeyPair] = Field(default_factory=dict)
    replication_regions: list[PQCRegion] = Field(default_factory=list)
    last_sync: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def add_key(self, key: PQCKeyPair) -> None:
        self.keys[key.key_id] = key
        self.last_sync = datetime.now(timezone.utc)

    def get_key(self, key_id: str) -> PQCKeyPair | None:
        return self.keys.get(key_id)

    def remove_expired_keys(self) -> int:
        expired = [key_id for key_id, key in self.keys.items() if key.is_expired()]
        for key_id in expired:
            del self.keys[key_id]
        if expired:
            self.last_sync = datetime.now(timezone.utc)
        return len(expired)


class GlobalPQCManager:
    """Execute PQC operations subject to caller-supplied regional policy."""

    def __init__(self, config: GlobalPQCConfiguration):
        self.config = config
        self.providers = {
            PQCAlgorithmType.ML_KEM: MLKEMAlgorithm(),
            PQCAlgorithmType.ML_DSA: MLDSAAlgorithm(),
        }
        self.key_stores = {
            region: PQCKeyStore(store_id=f"store-{region.value}", region=region)
            for region in PQCRegion
        }

    def get_regional_policy(self, region: PQCRegion) -> RegionalPQCPolicy | None:
        return next((policy for policy in self.config.regional_policies if policy.region == region), None)

    def require_regional_policy(self, region: PQCRegion) -> RegionalPQCPolicy:
        policy = self.get_regional_policy(region)
        if policy is None:
            raise PQCPolicyRequired(
                f"no authoritative PQC policy was supplied for {region.value}; compliance cannot be inferred"
            )
        return policy

    def _default_for_purpose(self, purpose: str) -> PQCAlgorithmType:
        if purpose == "encryption":
            return self.config.default_kem_algorithm
        if purpose == "signature":
            return self.config.default_signature_algorithm
        raise ValueError("purpose must be 'encryption' or 'signature'")

    def select_algorithm(
        self,
        region: PQCRegion,
        purpose: str = "encryption",
    ) -> tuple[PQCAlgorithmType, PQCSecurityLevel]:
        algorithm = self._default_for_purpose(purpose)
        policy = self.get_regional_policy(region)
        level = self.config.default_security_level
        if policy is not None:
            level = max(level, policy.minimum_security_level, key=lambda item: item.value)
            if algorithm not in policy.allowed_algorithms:
                if not self.config.allow_algorithm_negotiation:
                    raise PQCUnsupportedAlgorithm(
                        f"{algorithm.value} is not allowed by policy {policy.authority} for {region.value}"
                    )
                admitted = [
                    candidate
                    for candidate in policy.allowed_algorithms
                    if candidate in self.providers
                    and ((purpose == "encryption" and candidate is PQCAlgorithmType.ML_KEM)
                         or (purpose == "signature" and candidate is PQCAlgorithmType.ML_DSA))
                ]
                if not admitted:
                    raise PQCUnsupportedAlgorithm(
                        f"policy {policy.authority} allows no admitted {purpose} algorithm"
                    )
                algorithm = admitted[0]
        if algorithm not in self.providers:
            raise PQCUnsupportedAlgorithm(f"no admitted provider for {algorithm.value}")
        return algorithm, level

    def verify_regional_policy(
        self,
        region: PQCRegion,
        algorithm: PQCAlgorithmType,
        security_level: PQCSecurityLevel,
    ) -> bool:
        """Verify only the technical algorithm/level predicates supplied by policy."""

        policy = self.require_regional_policy(region)
        return algorithm in policy.allowed_algorithms and security_level.value >= policy.minimum_security_level.value

    def generate_regional_keypair(self, region: PQCRegion, purpose: str = "encryption") -> PQCKeyPair:
        algorithm, security_level = self.select_algorithm(region, purpose)
        if self.get_regional_policy(region) is not None and not self.verify_regional_policy(
            region, algorithm, security_level
        ):
            raise PQCUnsupportedAlgorithm(f"selected parameters violate policy for {region.value}")
        keypair = self.providers[algorithm].generate_keypair(security_level)
        keypair.metadata.update({"region": region.value, "purpose": purpose})
        policy = self.get_regional_policy(region)
        if policy is not None:
            keypair.metadata.update(
                {
                    "policy_authority": policy.authority,
                    "policy_observed_at": policy.observed_at.isoformat(),
                    "policy_framework_ids": [framework.value for framework in policy.compliance_frameworks],
                }
            )
        self.key_stores[region].add_key(keypair)
        return keypair

    def encrypt_for_region(
        self,
        plaintext: bytes,
        recipient_key_id: str,
        sender_region: PQCRegion,
        recipient_region: PQCRegion,
    ) -> PQCCiphertext:
        recipient_key = self.key_stores[recipient_region].get_key(recipient_key_id)
        if recipient_key is None:
            raise KeyError(f"recipient key {recipient_key_id!r} not found in {recipient_region.value}")
        if recipient_key.algorithm is not PQCAlgorithmType.ML_KEM:
            raise PQCUnsupportedAlgorithm("recipient key is not an admitted ML-KEM encryption key")
        recipient_policy = self.get_regional_policy(recipient_region)
        if recipient_policy is not None and not self.verify_regional_policy(
            recipient_region, recipient_key.algorithm, recipient_key.security_level
        ):
            raise PQCUnsupportedAlgorithm("recipient key no longer satisfies regional policy")
        ciphertext = self.providers[PQCAlgorithmType.ML_KEM].encrypt(plaintext, recipient_key.public_key)
        sender_policy = self.get_regional_policy(sender_region)
        ciphertext.metadata.update(
            {
                "sender_region": sender_region.value,
                "recipient_region": recipient_region.value,
                "sender_policy_authority": sender_policy.authority if sender_policy else None,
                "recipient_policy_authority": recipient_policy.authority if recipient_policy else None,
            }
        )
        return ciphertext

    def decrypt_in_region(self, ciphertext: PQCCiphertext, key_id: str, region: PQCRegion) -> bytes:
        keypair = self.key_stores[region].get_key(key_id)
        if keypair is None or keypair.private_key is None:
            raise KeyError(f"private key {key_id!r} not available in {region.value}")
        if keypair.algorithm is not PQCAlgorithmType.ML_KEM:
            raise PQCUnsupportedAlgorithm("key is not an admitted ML-KEM encryption key")
        return self.providers[PQCAlgorithmType.ML_KEM].decrypt(ciphertext, keypair.private_key)

    def sign_in_region(self, message: bytes, key_id: str, region: PQCRegion) -> PQCSignature:
        keypair = self.key_stores[region].get_key(key_id)
        if keypair is None or keypair.private_key is None:
            raise KeyError(f"private key {key_id!r} not available in {region.value}")
        if keypair.algorithm is not PQCAlgorithmType.ML_DSA:
            raise PQCUnsupportedAlgorithm("key is not an admitted ML-DSA signing key")
        return self.providers[PQCAlgorithmType.ML_DSA].sign(message, keypair.private_key)

    def verify_in_region(self, message: bytes, signature: PQCSignature, key_id: str, region: PQCRegion) -> bool:
        keypair = self.key_stores[region].get_key(key_id)
        if keypair is None or keypair.algorithm is not PQCAlgorithmType.ML_DSA:
            return False
        return self.providers[PQCAlgorithmType.ML_DSA].verify(message, signature, keypair.public_key)

    def get_global_readiness_report(self) -> dict[str, Any]:
        """Report observed key/policy state without manufacturing compliance readiness."""

        regions: dict[str, Any] = {}
        for region in PQCRegion:
            policy = self.get_regional_policy(region)
            store = self.key_stores[region]
            regions[region.value] = {
                "key_count": len(store.keys),
                "policy_supplied": policy is not None,
                "policy_authority": policy.authority if policy else None,
                "policy_observed_at": policy.observed_at.isoformat() if policy else None,
                "admitted_key_count": sum(
                    1 for key in store.keys.values() if key.algorithm in self.providers and not key.is_expired()
                ),
            }
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "regions": regions,
            "regions_with_policy": sum(1 for item in regions.values() if item["policy_supplied"]),
            "regions_with_admitted_keys": sum(1 for item in regions.values() if item["admitted_key_count"] > 0),
        }


def create_default_regional_policies() -> list[RegionalPQCPolicy]:
    """Refuse to manufacture jurisdiction policy from stale library defaults."""

    raise PQCPolicyRequired(
        "DSLModel does not embed default jurisdictional PQC policies; supply policies with authority and observed_at"
    )
