from __future__ import annotations

from datetime import datetime, timezone

import pytest

from dslmodel.pqc.algorithms import FalconAlgorithm, MLDSAAlgorithm, MLKEMAlgorithm
from dslmodel.pqc.core import PQCOperationError, PQCSecurityLevel, PQCUnsupportedAlgorithm
from dslmodel.pqc.global_manager import (
    GlobalPQCConfiguration,
    GlobalPQCManager,
    PQCAlgorithmType,
    PQCPolicyRequired,
    PQCRegion,
    RegionalPQCPolicy,
)


def test_mlkem_encrypt_decrypt_roundtrip_and_tamper_refusal() -> None:
    provider = MLKEMAlgorithm()
    keypair = provider.generate_keypair(PQCSecurityLevel.LEVEL_3)
    assert keypair.private_key is not None
    ciphertext = provider.encrypt(b"secret payload", keypair.public_key)
    assert provider.decrypt(ciphertext, keypair.private_key) == b"secret payload"

    tampered = ciphertext.model_copy(update={"ciphertext": ciphertext.ciphertext[:-1] + bytes([ciphertext.ciphertext[-1] ^ 1])})
    with pytest.raises(PQCOperationError):
        provider.decrypt(tampered, keypair.private_key)


def test_mldsa_sign_verify_and_wrong_message_falsifier() -> None:
    provider = MLDSAAlgorithm()
    keypair = provider.generate_keypair(PQCSecurityLevel.LEVEL_3)
    assert keypair.private_key is not None
    signature = provider.sign(b"authenticated message", keypair.private_key)
    assert provider.verify(b"authenticated message", signature, keypair.public_key)
    assert not provider.verify(b"different message", signature, keypair.public_key)


def test_historical_unverified_algorithm_is_explicitly_refused() -> None:
    with pytest.raises(PQCUnsupportedAlgorithm):
        FalconAlgorithm().generate_keypair(PQCSecurityLevel.LEVEL_1)


def test_manager_requires_authority_for_compliance_claims() -> None:
    manager = GlobalPQCManager(GlobalPQCConfiguration())
    with pytest.raises(PQCPolicyRequired):
        manager.verify_regional_policy(PQCRegion.EUROPE, PQCAlgorithmType.ML_KEM, PQCSecurityLevel.LEVEL_3)


def test_manager_routes_encryption_through_policy_and_real_provider() -> None:
    policy = RegionalPQCPolicy(
        region=PQCRegion.EUROPE,
        allowed_algorithms=[PQCAlgorithmType.ML_KEM, PQCAlgorithmType.ML_DSA],
        minimum_security_level=PQCSecurityLevel.LEVEL_3,
        authority="test-policy-v1",
        observed_at=datetime.now(timezone.utc),
    )
    manager = GlobalPQCManager(GlobalPQCConfiguration(regional_policies=[policy]))
    keypair = manager.generate_regional_keypair(PQCRegion.EUROPE, "encryption")
    ciphertext = manager.encrypt_for_region(
        b"cross-region payload",
        keypair.key_id,
        PQCRegion.EUROPE,
        PQCRegion.EUROPE,
    )
    assert manager.decrypt_in_region(ciphertext, keypair.key_id, PQCRegion.EUROPE) == b"cross-region payload"
    assert ciphertext.metadata["recipient_policy_authority"] == "test-policy-v1"
