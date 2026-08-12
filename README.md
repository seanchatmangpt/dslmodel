# DSLModel

DSLModel is a bounded Python 3.12 package for deterministic OpenAPI model manufacture, replayable artifact evidence, dependency-light document extraction, composable data transformations, and optional standardized post-quantum cryptography.

## Product boundary

The wheel is built from an explicit file allowlist. Repository history and experimental source are preserved for inspection, but files outside that allowlist are not installed and do not acquire runtime standing merely by existing.

The always-installed surface is:

- `dsl`: the single console entry point;
- deterministic OpenAPI 3 component-schema to Pydantic v2 manufacture;
- strict semantic self-test/status and artifact receipt/replay;
- TXT/Markdown, DOCX, and EPUB text extraction;
- composable JSON fetch/process/atomic-persist verbs.

Two optional verifier closures are declared:

```bash
python -m pip install '.[readers]'  # adds pypdf for PDF extraction
python -m pip install '.[pqc]'      # adds cryptography for ML-KEM / ML-DSA
```

PDF extraction fails closed when the optional backend is absent. PQC operations fail closed when the cryptography backend is absent.

## Standing model

A capability is **ALIVE** only after its exact subject executes successfully. Importability, a workflow definition, a generated file, or a historical implementation is not execution proof.

Run:

```bash
dsl doctor --json --strict
dsl dsl status --json --strict
dsl dsl inventory --json
```

The inventory distinguishes the required CLI surface, implemented optional libraries, and historical command families that are `NOT_SHIPPED`.

## Deterministic OpenAPI manufacture

```bash
dsl dsl core openapi openapi.yaml --output models.py
dsl receipt models.py
```

The generator accepts local JSON/YAML OpenAPI documents, rejects unsupported external `$ref` targets, emits Pydantic v2 source, and returns an artifact digest.

## Document readers

```python
from dslmodel.readers import DocReader

text = DocReader("contract.docx").forward()
chapters = DocReader("book.epub").read_chunks(4000)
```

DOCX and EPUB use dependency-light ZIP/XML parsing. PDF extraction is provided only through the `[readers]` extra; no OCR or fake extraction result is substituted when selectable text cannot be extracted.

## Composable verbs

```python
from dslmodel.verbs import FetchData, ProcessData, SaveToFile

pipeline = FetchData(timeout=5) | ProcessData() | SaveToFile()
pipeline({"url": "https://example.invalid/data.json", "file_path": "output.json"})
```

Composition passes the first stage's returned context into the next stage. Network, JSON, type, and persistence failures are explicit `VerbExecutionError`s; output persistence uses temporary-file replacement rather than partial writes.

## Post-quantum cryptography

The `[pqc]` extra uses the `cryptography` backend for standardized ML-KEM and ML-DSA. ML-KEM derives a shared secret through real encapsulation/decapsulation and uses AES-256-GCM for authenticated payload encryption. ML-DSA signs and cryptographically verifies messages. Historical `KyberAlgorithm` and `DilithiumAlgorithm` names are compatibility aliases to the standardized implementations.

Falcon and SPHINCS+ identifiers remain readable for historical records, but DSLModel does not manufacture success for them: operations are explicitly refused until this repository owns an admitted backend and execution verifier.

Regional policy is caller-supplied evidence. DSLModel does not hard-code jurisdictional transition dates or infer legal/compliance standing from an algorithm name; policy records require an authority identifier and observation timestamp.

## Every-branch vacuity audit

`scripts/audit_vacuity.py` inspects the complete Git branch graph. It:

- enumerates every local/remote branch;
- scans every implementation-file occurrence and deduplicates identical Git blobs;
- detects pass/ellipsis-only bodies, non-interface `NotImplementedError`, swallowed exceptions, constant status/empty returns, explicit unfinished markers, and randomized validation-like functions;
- separates the canonical shipped/build surface from tests/generated examples, canonical preserved-but-not-shipped source, and historical-branch-only blobs;
- emits a machine-readable branch × path × blob receipt.

CI fails on high/critical findings in the canonical shipped/build surface. Historical findings remain visible in the report rather than being erased or silently counted as production code.

The `evolution-forge-implementation` branch is a concrete reason for this distinction: its unique historical work contains simulated/random validation and fitness results. Those values are evidence of an experimental branch, not proof that autonomous evolution succeeded, and that branch is not shipped by the production wheel.

## Verification

The pull-request gate executes the real distribution plus the optional verifier closures:

```bash
python -m pip install -e '.[test,pqc,readers]'
python -m pip check
python -m pytest --noconftest -o addopts= -q \
  tests/test_capabilities.py \
  tests/test_cli_modernization.py \
  tests/generators/test_openapi_models.py \
  tests/test_distribution_contract.py \
  tests/test_doc_reader.py \
  tests/test_verbs.py \
  tests/test_pqc.py \
  tests/test_vacuity_audit.py
python scripts/audit_vacuity.py --all-branches --canonical-branch <branch> --fail-on high
```

CI also builds a wheel, inspects its exact contents, installs it in a clean environment, verifies that historical evolution/swarm/Ollama modules are absent, and replays strict CLI receipts. The container build installs the package and runs strict execution checks during image construction. Pull requests build but do not publish images; tag/manual release paths are the only GHCR publication routes.

## Historical source policy

Historical source is retained as reversible evidence and design archaeology. A historical capability becomes shipped only after its dependency closure, authority boundary, behavioral verifier, receipt, and replay path are added to the explicit package boundary. Exclusion is not an assertion that old code is correct; it is a refusal to confuse preserved source with supported runtime.

## Security and actuation

The CLI core performs local model generation and artifact hashing. OpenAPI external references are refused. PR container verification has read-only repository authority. Package-write authority is reserved for explicit tag/manual release paths. See `SECURITY.md` for vulnerability reporting.

## License

MIT. See `LICENSE`.
