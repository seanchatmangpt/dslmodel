# DSLModel

DSLModel is a bounded Python 3.12 tool for deterministic OpenAPI 3 model manufacture and replayable execution evidence.

## Production standing

The production surface is deliberately small. A capability is **ALIVE** only after it is imported, mounted, and its verifier executes successfully. Historical source remains in the repository for reversible recovery, but it does not acquire production standing merely by existing.

| Surface | Standing | Evidence path |
| --- | --- | --- |
| `dsl core openapi` | ALIVE when `dsl selftest --strict` passes | Generates Pydantic v2 models, imports them, validates data, and exercises refusal behavior |
| `dsl evidence receipt` | ALIVE when replay succeeds | SHA-256 artifact identity plus mutation falsifier |
| `dsl selftest` | ALIVE when every admitted semantic check executes | Machine-readable receipts |
| `dsl status` / `dsl inventory` | ALIVE when strict status succeeds | Aggregate admitted/non-admitted inventory |
| Historical agent, telemetry, Ollama, Weaver, swarm, evolution, red-team, PQC, and worktree commands | UNSUPPORTED / NOT_ADMITTED | Preserved source only; no ambient execution authority |

Run `dsl dsl inventory --json` for the canonical capability boundary.

## Install

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install .
dsl --help
```

The installed distribution exposes exactly one console script: `dsl`. Legacy `jygen` metadata was removed because no `jygen` package is shipped by the wheel.

## Deterministic model manufacture

```bash
dsl dsl core openapi openapi.yaml --output models.py
dsl receipt models.py
```

The generator accepts local JSON/YAML OpenAPI documents, rejects unsupported external `$ref` targets, emits Pydantic v2 source, and returns an artifact digest.

## Verification

The pull-request gate installs the actual package and its declared dependencies before testing it. It does not substitute `PYTHONPATH=src` for a distribution install.

```bash
python -m pip install -e '.[test]'
python -m pip check
python -m pytest --noconftest -o addopts= -q \
  tests/test_capabilities.py \
  tests/test_cli_modernization.py \
  tests/generators/test_openapi_models.py \
  tests/test_distribution_contract.py
dsl doctor --json --strict
dsl dsl status --json --strict
```

The container build repeats the same boundary from an installed wheel-compatible package and runs strict execution checks during image construction. Pull requests build but do not publish images; tag/manual release paths are the only GHCR actuation routes.

## Legacy source policy

The repository contains a large historical experimentation graph. It is intentionally preserved rather than rewritten or represented as production-ready. The canonical CLI inventory is authoritative about what is admitted. A legacy capability becomes supported only after its dependency closure, authority boundary, execution verifier, receipt, and replay path are added to the admitted graph.

## Security and actuation

The admitted core performs local model generation and local artifact hashing. It has no LLM, GitHub, cloud, shell, remediation, deployment, or autonomous-agent actuation path. External references are refused by the OpenAPI generator. Container publication is controlled by GitHub Actions and is not performed for pull requests.

## License

MIT. See `LICENSE`.
