"""Deterministic OpenAPI 3 schema to Pydantic v2 model generation."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from keyword import iskeyword
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

import yaml


class OpenAPIGenerationError(ValueError):
    """Raised when an OpenAPI document cannot be deterministically rendered."""


_IDENTIFIER = re.compile(r"\W+")


def _class_name(value: str) -> str:
    parts = [part for part in _IDENTIFIER.split(value) if part]
    name = "".join(part[:1].upper() + part[1:] for part in parts) or "GeneratedModel"
    if name[0].isdigit():
        name = f"Model{name}"
    return name


def _field_name(value: str) -> tuple[str, str | None]:
    candidate = _IDENTIFIER.sub("_", value).strip("_") or "field"
    if candidate[0].isdigit():
        candidate = f"field_{candidate}"
    if iskeyword(candidate):
        candidate = f"{candidate}_"
    return candidate, value if candidate != value else None


def _enum_member(value: Any, index: int) -> str:
    candidate = _IDENTIFIER.sub("_", str(value)).strip("_").upper()
    if not candidate:
        candidate = f"VALUE_{index}"
    if candidate[0].isdigit():
        candidate = f"VALUE_{candidate}"
    if iskeyword(candidate.lower()):
        candidate = f"VALUE_{candidate}"
    return candidate


@dataclass(slots=True)
class OpenAPIModelGenerator:
    """Render every component schema in one OpenAPI document."""

    document: Mapping[str, Any]
    imports: set[str] = field(default_factory=set)
    model_names: list[str] = field(default_factory=list)

    @property
    def schemas(self) -> Mapping[str, Mapping[str, Any]]:
        schemas = self.document.get("components", {}).get("schemas", {})
        if not isinstance(schemas, Mapping) or not schemas:
            raise OpenAPIGenerationError("OpenAPI document has no components.schemas")
        invalid = [name for name, schema in schemas.items() if not isinstance(schema, Mapping)]
        if invalid:
            raise OpenAPIGenerationError(f"schemas must be objects: {', '.join(map(str, invalid))}")
        return schemas  # type: ignore[return-value]

    def _resolve_ref(self, ref: str) -> tuple[str, Mapping[str, Any]]:
        prefix = "#/components/schemas/"
        if not ref.startswith(prefix):
            raise OpenAPIGenerationError(f"unsupported external reference: {ref}")
        raw_name = ref.removeprefix(prefix)
        try:
            schema = self.schemas[raw_name]
        except KeyError as exc:
            raise OpenAPIGenerationError(f"unresolved schema reference: {ref}") from exc
        return _class_name(raw_name), schema

    def _flatten_object(
        self,
        schema: Mapping[str, Any],
        *,
        seen_refs: frozenset[str] = frozenset(),
    ) -> tuple[dict[str, Any], set[str], Any]:
        properties: dict[str, Any] = {}
        required: set[str] = set()
        additional: Any = schema.get("additionalProperties", False)

        ref = schema.get("$ref")
        if isinstance(ref, str):
            if ref in seen_refs:
                return properties, required, additional
            _, resolved = self._resolve_ref(ref)
            return self._flatten_object(resolved, seen_refs=seen_refs | {ref})

        for part in schema.get("allOf", []) or []:
            if not isinstance(part, Mapping):
                raise OpenAPIGenerationError("allOf entries must be schema objects")
            part_properties, part_required, part_additional = self._flatten_object(
                part,
                seen_refs=seen_refs,
            )
            properties.update(part_properties)
            required.update(part_required)
            if part_additional is not False:
                additional = part_additional

        direct_properties = schema.get("properties", {}) or {}
        if not isinstance(direct_properties, Mapping):
            raise OpenAPIGenerationError("schema properties must be an object")
        properties.update(direct_properties)
        required.update(str(name) for name in (schema.get("required", []) or []))
        return properties, required, additional

    def _union(self, schemas: Sequence[Any]) -> str:
        members = []
        for item in schemas:
            if not isinstance(item, Mapping):
                raise OpenAPIGenerationError("union entries must be schema objects")
            rendered = self._type_for(item)
            if rendered not in members:
                members.append(rendered)
        if not members:
            self.imports.add("Any")
            return "Any"
        if len(members) == 1:
            return members[0]
        return " | ".join(members)

    def _type_for(self, schema: Mapping[str, Any]) -> str:
        ref = schema.get("$ref")
        if isinstance(ref, str):
            result, _ = self._resolve_ref(ref)
        elif schema.get("oneOf"):
            result = self._union(schema["oneOf"])
        elif schema.get("anyOf"):
            result = self._union(schema["anyOf"])
        elif schema.get("allOf"):
            flattened, _, additional = self._flatten_object(schema)
            if flattened:
                self.imports.add("Any")
                result = "dict[str, Any]"
            elif isinstance(additional, Mapping):
                result = f"dict[str, {self._type_for(additional)}]"
            else:
                self.imports.add("Any")
                result = "dict[str, Any]"
        elif "enum" in schema:
            values = schema.get("enum") or []
            self.imports.add("Literal")
            result = f"Literal[{', '.join(repr(value) for value in values)}]"
        else:
            schema_type = schema.get("type")
            if isinstance(schema_type, list):
                members = [
                    self._type_for({**schema, "type": member})
                    for member in schema_type
                    if member != "null"
                ]
                if not members:
                    return "None"
                result = " | ".join(dict.fromkeys(members))
                if "null" in schema_type and "None" not in result:
                    result = f"{result} | None"
                return result

            if schema_type == "string" or schema_type is None:
                fmt = schema.get("format")
                if fmt == "date-time":
                    self.imports.add("datetime")
                    result = "datetime"
                elif fmt == "date":
                    self.imports.add("date")
                    result = "date"
                elif fmt == "time":
                    self.imports.add("time")
                    result = "time"
                elif fmt == "uuid":
                    self.imports.add("UUID")
                    result = "UUID"
                elif schema_type is None:
                    self.imports.add("Any")
                    result = "Any"
                else:
                    result = "str"
            elif schema_type == "integer":
                result = "int"
            elif schema_type == "number":
                result = "float"
            elif schema_type == "boolean":
                result = "bool"
            elif schema_type == "array":
                items = schema.get("items", {})
                if not isinstance(items, Mapping):
                    raise OpenAPIGenerationError("array items must be a schema object")
                result = f"list[{self._type_for(items)}]"
            elif schema_type == "object":
                additional = schema.get("additionalProperties")
                if isinstance(additional, Mapping):
                    result = f"dict[str, {self._type_for(additional)}]"
                else:
                    self.imports.add("Any")
                    result = "dict[str, Any]"
            elif schema_type == "null":
                result = "None"
            else:
                raise OpenAPIGenerationError(f"unsupported schema type: {schema_type!r}")

        if schema.get("nullable") and "None" not in result:
            result = f"{result} | None"
        return result

    @staticmethod
    def _field_arguments(schema: Mapping[str, Any], alias: str | None) -> list[str]:
        arguments: list[str] = []
        if alias:
            arguments.append(f"alias={alias!r}")
        mapping = {
            "description": "description",
            "title": "title",
            "minimum": "ge",
            "exclusiveMinimum": "gt",
            "maximum": "le",
            "exclusiveMaximum": "lt",
            "minLength": "min_length",
            "maxLength": "max_length",
            "pattern": "pattern",
            "minItems": "min_length",
            "maxItems": "max_length",
        }
        for source, target in mapping.items():
            if source in schema and not isinstance(schema[source], bool):
                arguments.append(f"{target}={schema[source]!r}")
        return arguments

    def _render_enum(self, name: str, schema: Mapping[str, Any]) -> str:
        self.imports.add("Enum")
        values = list(schema.get("enum") or [])
        if not values:
            raise OpenAPIGenerationError(f"enum {name} has no values")
        base = "str, Enum" if all(isinstance(value, str) for value in values) else "Enum"
        lines = [f"class {name}({base}):"]
        used: set[str] = set()
        for index, value in enumerate(values, start=1):
            member = _enum_member(value, index)
            while member in used:
                member = f"{member}_{index}"
            used.add(member)
            lines.append(f"    {member} = {value!r}")
        return "\n".join(lines)

    def _render_root_model(self, name: str, schema: Mapping[str, Any]) -> str:
        self.imports.add("RootModel")
        root_type = self._type_for(schema)
        self.model_names.append(name)
        return f"class {name}(RootModel[{root_type}]):\n    pass"

    def _render_model(self, raw_name: str, schema: Mapping[str, Any]) -> str:
        name = _class_name(raw_name)
        if "enum" in schema and not schema.get("properties"):
            return self._render_enum(name, schema)

        schema_type = schema.get("type")
        if schema_type not in (None, "object") and not schema.get("allOf"):
            return self._render_root_model(name, schema)

        properties, required, additional = self._flatten_object(schema)
        self.model_names.append(name)
        lines = [f"class {name}(BaseModel):"]
        if not properties:
            if additional is not False:
                lines.append("    model_config = {'extra': 'allow'}")
            else:
                lines.append("    pass")
            return "\n".join(lines)

        for raw_field, field_schema in properties.items():
            if not isinstance(field_schema, Mapping):
                raise OpenAPIGenerationError(f"property {raw_name}.{raw_field} must be an object")
            field_name, alias = _field_name(str(raw_field))
            annotation = self._type_for(field_schema)
            is_required = raw_field in required and "default" not in field_schema
            if not is_required and "None" not in annotation:
                annotation = f"{annotation} | None"
            default = "..." if is_required else repr(field_schema.get("default", None))
            arguments = self._field_arguments(field_schema, alias)
            field_call = ", ".join([default, *arguments])
            lines.append(f"    {field_name}: {annotation} = Field({field_call})")
        if additional is not False:
            lines.append("\n    model_config = {'extra': 'allow'}")
        return "\n".join(lines)

    def render(self) -> str:
        """Return stable Python source for all component schemas."""

        self.imports.clear()
        self.model_names.clear()
        class_names = [_class_name(str(name)) for name in self.schemas]
        duplicates = sorted({name for name in class_names if class_names.count(name) > 1})
        if duplicates:
            raise OpenAPIGenerationError(
                f"schema names collapse to duplicate Python identifiers: {', '.join(duplicates)}"
            )
        rendered = [self._render_model(str(name), schema) for name, schema in self.schemas.items()]

        import_lines = ["from __future__ import annotations", ""]
        if {"date", "datetime", "time"} & self.imports:
            names = ", ".join(sorted({"date", "datetime", "time"} & self.imports))
            import_lines.append(f"from datetime import {names}")
        if "Enum" in self.imports:
            import_lines.append("from enum import Enum")
        typing_names = sorted({"Any", "Literal"} & self.imports)
        if typing_names:
            import_lines.append(f"from typing import {', '.join(typing_names)}")
        if "UUID" in self.imports:
            import_lines.append("from uuid import UUID")

        pydantic_names = ["BaseModel", "Field"]
        if "RootModel" in self.imports:
            pydantic_names.append("RootModel")
        import_lines.append(f"from pydantic import {', '.join(pydantic_names)}")
        import_lines.append("")

        body = "\n\n\n".join(rendered)
        rebuild = ""
        if self.model_names:
            names = ", ".join(self.model_names)
            rebuild = (
                "\n\n\n# Resolve forward and circular references after every model exists.\n"
                f"for _model in ({names},):\n"
                "    _model.model_rebuild()\n"
                "del _model\n"
            )
        return "\n".join(import_lines) + body + rebuild


def load_openapi(path: Path) -> Mapping[str, Any]:
    """Load an OpenAPI JSON or YAML document."""

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OpenAPIGenerationError(f"cannot read {path}: {exc}") from exc
    try:
        document = json.loads(text) if path.suffix.lower() == ".json" else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise OpenAPIGenerationError(f"invalid OpenAPI document {path}: {exc}") from exc
    if not isinstance(document, Mapping):
        raise OpenAPIGenerationError("OpenAPI document root must be an object")
    return document


def generate_openapi_models(openapi_file: Path, output_file: Path) -> Path:
    """Generate a deterministic Pydantic module and return its path."""

    document = load_openapi(openapi_file)
    source = OpenAPIModelGenerator(document).render()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(source, encoding="utf-8")
    return output_file
