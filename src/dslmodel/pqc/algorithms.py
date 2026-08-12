"""Production PQC providers backed by pyca/cryptography.

ML-KEM provides key encapsulation and is combined with AES-256-GCM for payload
confidentiality/integrity. ML-DSA provides signatures. Historical Kyber and
Dilithium class names are compatibility aliases to the standardized algorithms.
Falcon and SPHINCS+ records remain readable but operations are explicitly
unsupported rather than returning fabricated cryptographic success.
"""

from __future__ import annotations

from hashlib import sha256
import importlib
import secrets
from typing import Any

from .core import (
    PQCAlgorithmType,
    PQCBackendUnavailable,
    PQCCiphertext,
    PQCKeyPair,
    PQCOperationError,
    PQCProvider,
    PQCSecurityLevel,
    PQCSignature,
    PQCUnsupportedAlgorithm,
)

_PRIVATE_MAGIC = b"DSLM-PQC1\x00"
_AAD_PREFIX = b"dslmodel:pqc:ml-kem+aes-256-gcm:v1:"

_KEM_PARAMETER_BY_LEVEL = {
    PQCSecurityLevel.LEVEL_1: "512",
    PQCSecurityLevel.LEVEL_3: "768",
    PQCSecurityLevel.LEVEL_5: "1024",
}
_KEM_PARAMETER_BY_PUBLIC_SIZE = {800: "512", 1184: "768", 1568: "1024"}
_KEM_PARAMETER_BY_CIPHERTEXT_SIZE = {768: "512", 1088: "768", 1568: "1024"}
_KEM_LEVEL_BY_PARAMETER = {value: key for key, value in _KEM_PARAMETER_BY_LEVEL.items()}

_DSA_PARAMETER_BY_LEVEL = {
    PQCSecurityLevel.LEVEL_2: "44",
    PQCSecurityLevel.LEVEL_3: "65",
    PQCSecurityLevel.LEVEL_5: "87",
}
_DSA_PARAMETER_BY_PUBLIC_SIZE = {1312: "44", 1952: "65", 2592: "87"}
_DSA_LEVEL_BY_PARAMETER = {value: key for key, value in _DSA_PARAMETER_BY_LEVEL.items()}


def _cryptography_modules() -> tuple[Any, Any, Any, Any]:
    try:
        mlkem = importlib.import_module("cryptography.hazmat.primitives.asymmetric.mlkem")
        mldsa = importlib.import_module("cryptography.hazmat.primitives.asymmetric.mldsa")
        aead = importlib.import_module("cryptography.hazmat.primitives.ciphers.aead")
        exceptions = importlib.import_module("cryptography.exceptions")
    except (ModuleNotFoundError, ImportError) as exc:
        raise PQCBackendUnavailable(
            "PQC operations require the optional backend; install 'dslmodel[pqc]'"
        ) from exc
    return mlkem, mldsa, aead, exceptions


def _private_envelope(parameter: str, raw_seed: bytes) -> bytes:
    encoded = parameter.encode("ascii")
    if len(encoded) > 8:
        raise ValueError("parameter identifier is too long")
    return _PRIVATE_MAGIC + bytes([len(encoded)]) + encoded + raw_seed


def _parse_private_envelope(payload: bytes) -> tuple[str, bytes]:
    if not payload.startswith(_PRIVATE_MAGIC) or len(payload) <= len(_PRIVATE_MAGIC):
        raise PQCOperationError("private key is not a DSLModel PQC v1 serialization")
    length_index = len(_PRIVATE_MAGIC)
    parameter_length = payload[length_index]
    parameter_start = length_index + 1
    parameter_end = parameter_start + parameter_length
    if parameter_end >= len(payload):
        raise PQCOperationError("private key serialization is truncated")
    try:
        parameter = payload[parameter_start:parameter_end].decode("ascii")
    except UnicodeDecodeError as exc:
        raise PQCOperationError("private key parameter identifier is invalid") from exc
    return parameter, payload[parameter_end:]


def _key_id(algorithm: PQCAlgorithmType, public_key: bytes) -> str:
    digest = sha256(algorithm.value.encode("ascii") + b"\x00" + public_key).hexdigest()
    return f"{algorithm.value}-{digest[:24]}"


def _kem_classes(parameter: str) -> tuple[type[Any], type[Any]]:
    mlkem, _, _, _ = _cryptography_modules()
    try:
        return (
            getattr(mlkem, f"MLKEM{parameter}PrivateKey"),
            getattr(mlkem, f"MLKEM{parameter}PublicKey"),
        )
    except AttributeError as exc:
        raise PQCBackendUnavailable(f"cryptography backend does not expose ML-KEM-{parameter}") from exc


def _dsa_classes(parameter: str) -> tuple[type[Any], type[Any]]:
    _, mldsa, _, _ = _cryptography_modules()
    try:
        return (
            getattr(mldsa, f"MLDSA{parameter}PrivateKey"),
            getattr(mldsa, f"MLDSA{parameter}PublicKey"),
        )
    except AttributeError as exc:
        raise PQCBackendUnavailable(f"cryptography backend does not expose ML-DSA-{parameter}") from exc


class MLKEMAlgorithm(PQCProvider):
    """ML-KEM key encapsulation plus AES-256-GCM payload encryption."""

    def generate_keypair(self, security_level: PQCSecurityLevel) -> PQCKeyPair:
        try:
            parameter = _KEM_PARAMETER_BY_LEVEL[security_level]
        except KeyError as exc:
            raise PQCUnsupportedAlgorithm(
                f"ML-KEM supports security levels {sorted(level.value for level in _KEM_PARAMETER_BY_LEVEL)}"
            ) from exc
        private_cls, _ = _kem_classes(parameter)
        try:
            private = private_cls.generate()
            public_bytes = private.public_key().public_bytes_raw()
            raw_seed = private.private_bytes_raw()
        except Exception as exc:
            raise PQCOperationError(f"ML-KEM-{parameter} key generation failed: {exc}") from exc
        return PQCKeyPair(
            algorithm=PQCAlgorithmType.ML_KEM,
            security_level=security_level,
            public_key=public_bytes,
            private_key=_private_envelope(parameter, raw_seed),
            key_id=_key_id(PQCAlgorithmType.ML_KEM, public_bytes),
            metadata={
                "standard": "FIPS 203",
                "parameter_set": f"ML-KEM-{parameter}",
                "private_format": "dslmodel-pqc-v1",
            },
        )

    def encrypt(self, plaintext: bytes, public_key: bytes) -> PQCCiphertext:
        try:
            parameter = _KEM_PARAMETER_BY_PUBLIC_SIZE[len(public_key)]
        except KeyError as exc:
            raise PQCOperationError(f"unsupported ML-KEM public key length: {len(public_key)}") from exc
        _, public_cls = _kem_classes(parameter)
        _, _, aead, _ = _cryptography_modules()
        try:
            public = public_cls.from_public_bytes(public_key)
            shared_secret, kem_ciphertext = public.encapsulate()
            nonce = secrets.token_bytes(12)
            aad = _AAD_PREFIX + parameter.encode("ascii")
            payload = aead.AESGCM(shared_secret).encrypt(nonce, plaintext, aad)
        except Exception as exc:
            raise PQCOperationError(f"ML-KEM-{parameter} encryption failed: {exc}") from exc
        return PQCCiphertext(
            algorithm=PQCAlgorithmType.ML_KEM,
            ciphertext=payload,
            encapsulated_key=kem_ciphertext,
            recipient_key_id=_key_id(PQCAlgorithmType.ML_KEM, public_key),
            metadata={
                "standard": "FIPS 203",
                "parameter_set": f"ML-KEM-{parameter}",
                "aead": "AES-256-GCM",
                "nonce": nonce.hex(),
                "format": "dslmodel-pqc-ciphertext-v1",
            },
        )

    def decrypt(self, ciphertext: PQCCiphertext, private_key: bytes) -> bytes:
        if ciphertext.algorithm is not PQCAlgorithmType.ML_KEM:
            raise PQCOperationError(f"ciphertext algorithm is {ciphertext.algorithm.value}, expected ml_kem")
        if ciphertext.encapsulated_key is None:
            raise PQCOperationError("ML-KEM ciphertext is missing encapsulation material")
        try:
            parameter = _KEM_PARAMETER_BY_CIPHERTEXT_SIZE[len(ciphertext.encapsulated_key)]
        except KeyError as exc:
            raise PQCOperationError(
                f"unsupported ML-KEM ciphertext length: {len(ciphertext.encapsulated_key)}"
            ) from exc
        serialized_parameter, raw_seed = _parse_private_envelope(private_key)
        if serialized_parameter != parameter:
            raise PQCOperationError(
                f"private key parameter ML-KEM-{serialized_parameter} does not match ciphertext ML-KEM-{parameter}"
            )
        private_cls, _ = _kem_classes(parameter)
        _, _, aead, exceptions = _cryptography_modules()
        try:
            nonce_hex = ciphertext.metadata["nonce"]
            nonce = bytes.fromhex(str(nonce_hex))
            if len(nonce) != 12:
                raise ValueError("AES-GCM nonce must be 12 bytes")
            private = private_cls.from_seed_bytes(raw_seed)
            shared_secret = private.decapsulate(ciphertext.encapsulated_key)
            aad = _AAD_PREFIX + parameter.encode("ascii")
            return aead.AESGCM(shared_secret).decrypt(nonce, ciphertext.ciphertext, aad)
        except (exceptions.InvalidTag, KeyError, ValueError, TypeError) as exc:
            raise PQCOperationError("ciphertext authentication/decapsulation failed") from exc
        except Exception as exc:
            raise PQCOperationError(f"ML-KEM-{parameter} decryption failed: {exc}") from exc

    def sign(self, message: bytes, private_key: bytes) -> PQCSignature:
        del message, private_key
        raise PQCUnsupportedAlgorithm("ML-KEM is a key-encapsulation algorithm; use ML-DSA for signatures")

    def verify(self, message: bytes, signature: PQCSignature, public_key: bytes) -> bool:
        del message, signature, public_key
        raise PQCUnsupportedAlgorithm("ML-KEM is a key-encapsulation algorithm; use ML-DSA for signatures")


class MLDSAAlgorithm(PQCProvider):
    """ML-DSA signing and verification backed by FIPS 204 implementations."""

    def generate_keypair(self, security_level: PQCSecurityLevel) -> PQCKeyPair:
        try:
            parameter = _DSA_PARAMETER_BY_LEVEL[security_level]
        except KeyError as exc:
            raise PQCUnsupportedAlgorithm(
                f"ML-DSA supports security levels {sorted(level.value for level in _DSA_PARAMETER_BY_LEVEL)}"
            ) from exc
        private_cls, _ = _dsa_classes(parameter)
        try:
            private = private_cls.generate()
            public_bytes = private.public_key().public_bytes_raw()
            raw_seed = private.private_bytes_raw()
        except Exception as exc:
            raise PQCOperationError(f"ML-DSA-{parameter} key generation failed: {exc}") from exc
        return PQCKeyPair(
            algorithm=PQCAlgorithmType.ML_DSA,
            security_level=security_level,
            public_key=public_bytes,
            private_key=_private_envelope(parameter, raw_seed),
            key_id=_key_id(PQCAlgorithmType.ML_DSA, public_bytes),
            metadata={
                "standard": "FIPS 204",
                "parameter_set": f"ML-DSA-{parameter}",
                "private_format": "dslmodel-pqc-v1",
            },
        )

    def sign(self, message: bytes, private_key: bytes) -> PQCSignature:
        parameter, raw_seed = _parse_private_envelope(private_key)
        if parameter not in _DSA_LEVEL_BY_PARAMETER:
            raise PQCOperationError(f"private key parameter is not an admitted ML-DSA set: {parameter}")
        private_cls, _ = _dsa_classes(parameter)
        try:
            private = private_cls.from_seed_bytes(raw_seed)
            public_bytes = private.public_key().public_bytes_raw()
            signature = private.sign(message)
        except Exception as exc:
            raise PQCOperationError(f"ML-DSA-{parameter} signing failed: {exc}") from exc
        return PQCSignature(
            algorithm=PQCAlgorithmType.ML_DSA,
            signature=signature,
            message_hash=sha256(message).hexdigest(),
            key_id=_key_id(PQCAlgorithmType.ML_DSA, public_bytes),
            metadata={"standard": "FIPS 204", "parameter_set": f"ML-DSA-{parameter}"},
        )

    def verify(self, message: bytes, signature: PQCSignature, public_key: bytes) -> bool:
        if signature.algorithm is not PQCAlgorithmType.ML_DSA:
            return False
        try:
            parameter = _DSA_PARAMETER_BY_PUBLIC_SIZE[len(public_key)]
        except KeyError:
            return False
        _, public_cls = _dsa_classes(parameter)
        _, _, _, exceptions = _cryptography_modules()
        try:
            public = public_cls.from_public_bytes(public_key)
            public.verify(signature.signature, message)
        except exceptions.InvalidSignature:
            return False
        except (ValueError, TypeError):
            return False
        except Exception as exc:
            raise PQCOperationError(f"ML-DSA-{parameter} verification failed: {exc}") from exc
        expected_key_id = _key_id(PQCAlgorithmType.ML_DSA, public_key)
        return signature.key_id == expected_key_id and signature.message_hash == sha256(message).hexdigest()

    def encrypt(self, plaintext: bytes, public_key: bytes) -> PQCCiphertext:
        del plaintext, public_key
        raise PQCUnsupportedAlgorithm("ML-DSA is a signature algorithm; use ML-KEM for encryption")

    def decrypt(self, ciphertext: PQCCiphertext, private_key: bytes) -> bytes:
        del ciphertext, private_key
        raise PQCUnsupportedAlgorithm("ML-DSA is a signature algorithm; use ML-KEM for encryption")


class _UnsupportedHistoricalSignature(PQCProvider):
    name = "historical signature algorithm"

    def _refuse(self) -> None:
        raise PQCUnsupportedAlgorithm(
            f"{self.name} has no admitted production backend in DSLModel; use ML-DSA"
        )

    def generate_keypair(self, security_level: PQCSecurityLevel) -> PQCKeyPair:
        del security_level
        self._refuse()
        raise AssertionError("unreachable")

    def sign(self, message: bytes, private_key: bytes) -> PQCSignature:
        del message, private_key
        self._refuse()
        raise AssertionError("unreachable")

    def verify(self, message: bytes, signature: PQCSignature, public_key: bytes) -> bool:
        del message, signature, public_key
        self._refuse()
        raise AssertionError("unreachable")

    def encrypt(self, plaintext: bytes, public_key: bytes) -> PQCCiphertext:
        del plaintext, public_key
        self._refuse()
        raise AssertionError("unreachable")

    def decrypt(self, ciphertext: PQCCiphertext, private_key: bytes) -> bytes:
        del ciphertext, private_key
        self._refuse()
        raise AssertionError("unreachable")


class FalconAlgorithm(_UnsupportedHistoricalSignature):
    name = "Falcon"


class SPHINCSPlusAlgorithm(_UnsupportedHistoricalSignature):
    name = "SPHINCS+"


# Compatibility symbols for callers using pre-standard DSLModel names.
KyberAlgorithm = MLKEMAlgorithm
DilithiumAlgorithm = MLDSAAlgorithm
