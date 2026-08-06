# DSLModel ERRC Modernization

## Standing before this change

The advertised command surface was `PARTIAL_ALIVE`:

- importing `dslmodel` eagerly initialized text/DSPy behavior and imported unrelated subsystems;
- importing `dslmodel.commands` eagerly imported a fixed subset of heavy command modules;
- one `ImportError` in `consolidated_cli.py` set a global `FULL_IMPORTS = False`, disabling every consolidated capability;
- many consolidated commands printed that a feature was “available” but never delegated to its implementation;
- `dsl openapi` generated only the schema named `Pet`, required an LLM, slept, and emitted no deterministic artifact receipt.

## ERRC decisions

| Action | Decision |
|---|---|
| **Eliminate** | Import-time DSPy initialization, global warning suppression, all-or-nothing `FULL_IMPORTS`, placeholder “available” commands, hard-coded `Pet` filtering, and mandatory LLM use for OpenAPI conversion. |
| **Reduce** | Root-module coupling, eager optional imports, duplicated wrapper logic, and failure blast radius. |
| **Raise** | Capability evidence from prose/print statements to typed per-module standing, deterministic SHA-256 receipt identities, strict JSON health output, real Typer application mounting, and executable generated-model tests. |
| **Create** | Side-effect-free lazy public exports, a capability admission registry, root and consolidated doctor/status commands, and deterministic OpenAPI 3 → Pydantic v2 generation for objects, arrays, enums, references, unions, constraints, aliases, `allOf`, root models, and circular references. |

## Operational boundaries

- Importing one capability never actuates another capability.
- Missing external dependencies are `UNSUPPORTED`; missing/broken internal command modules are `BUILD_BROKEN`.
- A capability is `ALIVE` only after its module imports, exposes a Typer app, and mounts successfully.
- OpenAPI generation is offline and deterministic. External `$ref` transport is intentionally refused because it is not admitted into the local document boundary.
- Legacy root command names remain available whenever their individual modules are admitted.

## Replay

```bash
python -m compileall -q src tests
PYTHONPATH=src pytest -q tests/test_capabilities.py tests/test_cli_modernization.py tests/generators/test_openapi_models.py
PYTHONPATH=src python -m dslmodel.cli doctor --json
PYTHONPATH=src python -m dslmodel.cli dsl status --json
```
