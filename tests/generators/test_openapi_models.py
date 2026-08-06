from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from dslmodel.generators.openapi_models import (
    OpenAPIGenerationError,
    OpenAPIModelGenerator,
    generate_openapi_models,
)


def sample_document() -> dict:
    return {
        "openapi": "3.1.0",
        "info": {"title": "test", "version": "1"},
        "components": {
            "schemas": {
                "Status": {"type": "string", "enum": ["ready", "blocked"]},
                "Pet": {
                    "type": "object",
                    "required": ["name", "status"],
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                        "status": {"$ref": "#/components/schemas/Status"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "class": {"type": "string", "description": "reserved alias"},
                    },
                },
                "OwnedPet": {
                    "allOf": [
                        {"$ref": "#/components/schemas/Pet"},
                        {
                            "type": "object",
                            "required": ["owner_id"],
                            "properties": {
                                "owner_id": {"type": "string", "format": "uuid"}
                            },
                        },
                    ]
                },
                "Node": {
                    "type": "object",
                    "required": ["value"],
                    "properties": {
                        "value": {"type": "string"},
                        "next": {"$ref": "#/components/schemas/Node", "nullable": True},
                    },
                },
            }
        },
    }


def test_generator_renders_all_schemas_and_executes() -> None:
    source = OpenAPIModelGenerator(sample_document()).render()
    namespace: dict = {}
    exec(compile(source, "generated_models.py", "exec"), namespace)

    Status = namespace["Status"]
    Pet = namespace["Pet"]
    OwnedPet = namespace["OwnedPet"]
    Node = namespace["Node"]

    pet = Pet(name="Mark", status=Status.READY, tags=["dog"], **{"class": "dachshund"})
    assert pet.class_ == "dachshund"
    assert pet.model_dump(by_alias=True)["class"] == "dachshund"

    owned = OwnedPet(
        name="Mark",
        status="ready",
        owner_id="12345678-1234-5678-1234-567812345678",
    )
    assert str(owned.owner_id) == "12345678-1234-5678-1234-567812345678"

    node = Node(value="root", next={"value": "leaf"})
    assert node.next.value == "leaf"

    with pytest.raises(ValidationError):
        Pet(name="", status="ready")


def test_generation_is_deterministic() -> None:
    first = OpenAPIModelGenerator(sample_document()).render()
    second = OpenAPIModelGenerator(sample_document()).render()
    assert first == second


def test_external_refs_are_refused() -> None:
    document = {
        "components": {
            "schemas": {
                "Broken": {
                    "type": "object",
                    "properties": {"value": {"$ref": "https://example.com/schema.json"}},
                }
            }
        }
    }
    with pytest.raises(OpenAPIGenerationError, match="external reference"):
        OpenAPIModelGenerator(document).render()


def test_generate_openapi_models_writes_output(tmp_path: Path) -> None:
    input_file = tmp_path / "openapi.json"
    output_file = tmp_path / "models.py"
    import json

    input_file.write_text(json.dumps(sample_document()), encoding="utf-8")
    result = generate_openapi_models(input_file, output_file)

    assert result == output_file
    assert output_file.read_text(encoding="utf-8").startswith("from __future__ import annotations")


def test_required_nullable_reference_is_preserved() -> None:
    document = sample_document()
    document["components"]["schemas"]["RequiredNullable"] = {
        "type": "object",
        "required": ["pet"],
        "properties": {
            "pet": {"$ref": "#/components/schemas/Pet", "nullable": True}
        },
    }
    source = OpenAPIModelGenerator(document).render()
    namespace: dict = {}
    exec(compile(source, "nullable_models.py", "exec"), namespace)
    assert namespace["RequiredNullable"](pet=None).pet is None


def test_colliding_python_class_names_are_refused() -> None:
    document = {
        "components": {
            "schemas": {
                "foo-bar": {"type": "object"},
                "foo bar": {"type": "object"},
            }
        }
    }
    with pytest.raises(OpenAPIGenerationError, match="duplicate Python identifiers"):
        OpenAPIModelGenerator(document).render()


def test_additional_properties_semantics_are_preserved() -> None:
    document = {
        "components": {
            "schemas": {
                "OpenObject": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                },
                "ClosedObject": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {"name": {"type": "string"}},
                },
                "Counters": {
                    "type": "object",
                    "additionalProperties": {"type": "integer", "minimum": 0},
                },
            }
        }
    }
    namespace: dict = {}
    exec(compile(OpenAPIModelGenerator(document).render(), "extra_models.py", "exec"), namespace)

    assert namespace["OpenObject"](name="x", extra=1).model_extra == {"extra": 1}
    with pytest.raises(ValidationError):
        namespace["ClosedObject"](name="x", extra=1)
    assert namespace["Counters"]({"ok": 1}).root == {"ok": 1}
    with pytest.raises(ValidationError):
        namespace["Counters"]({"bad": -1})


def test_required_property_with_default_remains_required() -> None:
    document = {
        "components": {
            "schemas": {
                "RequiredDefault": {
                    "type": "object",
                    "required": ["mode"],
                    "properties": {"mode": {"type": "string", "default": "safe"}},
                }
            }
        }
    }
    namespace: dict = {}
    exec(compile(OpenAPIModelGenerator(document).render(), "required_models.py", "exec"), namespace)
    with pytest.raises(ValidationError):
        namespace["RequiredDefault"]()
    assert namespace["RequiredDefault"](mode="safe").mode == "safe"


def test_openapi_30_boolean_exclusive_bounds() -> None:
    document = {
        "components": {
            "schemas": {
                "Range": {
                    "type": "object",
                    "required": ["value"],
                    "properties": {
                        "value": {
                            "type": "number",
                            "minimum": 0,
                            "exclusiveMinimum": True,
                            "maximum": 10,
                            "exclusiveMaximum": True,
                        }
                    },
                }
            }
        }
    }
    namespace: dict = {}
    exec(compile(OpenAPIModelGenerator(document).render(), "range_models.py", "exec"), namespace)
    assert namespace["Range"](value=5).value == 5
    with pytest.raises(ValidationError):
        namespace["Range"](value=0)
    with pytest.raises(ValidationError):
        namespace["Range"](value=10)
