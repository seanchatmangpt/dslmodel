"""Language binding manufacture for the admitted DSLModel PQC backend.

Historically this module emitted random-byte crypto clients for several
languages. The current implementation emits one dependency-closed Python
binding backed by DSLModel's verified ML-KEM/ML-DSA providers and explicitly
refuses language targets for which this repository has no compiled verifier.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .core import PQCUnsupportedAlgorithm


class PQCLanguageBinding(BaseModel):
    """Receipt describing one generated, verifier-owned language binding."""

    model_config = ConfigDict(extra="forbid")
    language: str
    output_file: str
    dependencies: dict[str, str] = Field(default_factory=dict)

    def generate_code(self, context: dict[str, Any] | None = None) -> str:
        del context
        if self.language != "python":
            raise PQCUnsupportedAlgorithm(
                f"{self.language} PQC generation is not admitted: no repository-owned compile/runtime verifier exists"
            )
        return PYTHON_BINDING


class MultiLanguagePQCGenerator:
    """Generate only language bindings with executable proof in this repository."""

    LANGUAGE_CONFIGS = {
        "python": {
            "output": "pqc_client.py",
            "dependencies": {
                "dslmodel": ">=2024.12.22.2",
                "cryptography": ">=49,<50",
            },
        }
    }
    REFUSED_LANGUAGES = {"rust", "go", "typescript", "java"}

    def generate_for_language(self, language: str, context: dict[str, Any] | None = None) -> str:
        normalized = language.strip().lower()
        if normalized in self.REFUSED_LANGUAGES:
            raise PQCUnsupportedAlgorithm(
                f"{normalized} PQC generation is refused until a compile/runtime verifier is owned by DSLModel"
            )
        try:
            config = self.LANGUAGE_CONFIGS[normalized]
        except KeyError as exc:
            raise ValueError(f"unknown language: {language}") from exc
        binding = PQCLanguageBinding(
            language=normalized,
            output_file=config["output"],
            dependencies=config["dependencies"],
        )
        return binding.generate_code(context)

    def generate_all_languages(self, context: dict[str, Any] | None, output_dir: Path) -> dict[str, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated: dict[str, Path] = {}
        for language, config in self.LANGUAGE_CONFIGS.items():
            target = output_dir / config["output"]
            target.write_text(self.generate_for_language(language, context), encoding="utf-8")
            generated[language] = target
        self._generate_package_files(output_dir)
        return generated

    @staticmethod
    def _generate_package_files(output_dir: Path) -> None:
        pyproject = dedent(
            """
            [build-system]
            requires = ["hatchling>=1.27,<2"]
            build-backend = "hatchling.build"

            [project]
            name = "dslmodel-pqc-client"
            version = "1.0.0"
            requires-python = ">=3.12"
            dependencies = [
              "dslmodel>=2024.12.22.2",
              "cryptography>=49,<50",
            ]
            """
        ).strip() + "\n"
        (output_dir / "pyproject.toml").write_text(pyproject, encoding="utf-8")


PYTHON_BINDING = dedent(
    '''
    """Generated DSLModel PQC client backed by ML-KEM and ML-DSA."""

    from dslmodel.pqc.algorithms import MLDSAAlgorithm, MLKEMAlgorithm
    from dslmodel.pqc.core import PQCSecurityLevel


    class PQCClient:
        def __init__(self) -> None:
            self.kem = MLKEMAlgorithm()
            self.signature = MLDSAAlgorithm()

        def generate_encryption_keypair(self, level: int = 3):
            return self.kem.generate_keypair(PQCSecurityLevel(level))

        def encrypt(self, plaintext: bytes, public_key: bytes):
            return self.kem.encrypt(plaintext, public_key)

        def decrypt(self, ciphertext, private_key: bytes) -> bytes:
            return self.kem.decrypt(ciphertext, private_key)

        def generate_signing_keypair(self, level: int = 3):
            return self.signature.generate_keypair(PQCSecurityLevel(level))

        def sign(self, message: bytes, private_key: bytes):
            return self.signature.sign(message, private_key)

        def verify(self, message: bytes, signature, public_key: bytes) -> bool:
            return self.signature.verify(message, signature, public_key)
    '''
).strip() + "\n"
