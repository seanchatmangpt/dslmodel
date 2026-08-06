# DSLModel 80/20 ERRC Modernization

## Final admitted standing

The canonical product surface is `ALIVE` only after observed execution. Import
or mounting alone is `PARTIAL_ALIVE`; it cannot crown a capability.

The admitted surface contains five jobs:

1. `core.openapi` — deterministic OpenAPI 3 to executable Pydantic v2 manufacture;
2. `validate.selftest` — dependency-closed semantic self-play;
3. `evidence.receipt` — deterministic artifact identity and replay;
4. `system.status` — machine-readable aggregate standing;
5. `system.inventory` — admitted and non-admitted capability catalog.

Forty historical aliases and experimental/external-runtime integrations remain
in the repository for reversible recovery, but are `NOT_ADMITTED`. They do not
pollute product standing and are not mislabeled `ALIVE`, `UNSUPPORTED`, or
`BUILD_BROKEN` without exact execution evidence.

## ERRC decisions

| Action | Decision |
|---|---|
| **Eliminate** | Import-time DSPy initialization, global warning suppression, all-or-nothing imports, placeholder success commands, duplicate root aliases, LLM/network requirements for OpenAPI manufacture, and the devcontainer/Node CI dependency for the canonical verifier. |
| **Reduce** | The advertised CLI from roughly forty legacy surfaces to five high-value jobs; optional dependency blast radius; CI installation to the dependency-closed verifier pack. |
| **Raise** | `ALIVE` from import/mount evidence to successful verifier execution; strict status; deterministic artifact and capability receipts; drift falsification; executable generated-model checks. |
| **Create** | Canonical 80/20 CLI, non-admitted legacy inventory, semantic self-test pack, artifact receipt/replay commands, and direct Python 3.12 CI. |

## Evidence law

- `UNKNOWN` is not admitted.
- Import success is `PARTIAL_ALIVE`, not `ALIVE`.
- `ALIVE` requires import, mount, and successful verifier execution.
- Missing external dependencies are `UNSUPPORTED` only for admitted subjects.
- Historical surfaces outside the product boundary are `NOT_ADMITTED`, not failures.
- Receipt replay detects artifact mutation.
- Receipt identity binds algorithm, content digest, and size; transport paths are informational only.

## Replay

```bash
python -m compileall -q src tests
PYTHONPATH=src pytest -q \
  tests/test_capabilities.py \
  tests/test_cli_modernization.py \
  tests/generators/test_openapi_models.py
PYTHONPATH=src python -m dslmodel.cli doctor --json --strict
PYTHONPATH=src python -m dslmodel.cli dsl status --json --strict
```

Expected local result:

```text
25 passed
ALIVE
ALIVE
```
