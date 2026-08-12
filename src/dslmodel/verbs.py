"""Composable, deterministic DSL verbs.

Verbs are explicit transformations over a mutable context mapping. Composition
passes the output of each stage to the next stage and never converts failures
into an unusable base-class object.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, MutableMapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

Context = MutableMapping[str, Any]


class VerbExecutionError(RuntimeError):
    """Raised when a verb cannot complete its declared transformation."""


class DSLVerb(ABC):
    """Abstract context transformation that can be composed with ``|``."""

    def __init__(self, context: Context | None = None, **kwargs: Any) -> None:
        self.context: dict[str, Any] = dict(context or {})
        self.update_context(kwargs)

    @abstractmethod
    def __call__(self, context: Context) -> Context:
        """Execute the transformation and return the context for the next stage."""

    def __or__(self, other: "DSLVerb") -> "ComposeVerb":
        if not isinstance(other, DSLVerb):
            return NotImplemented
        return ComposeVerb(self, other)

    def update_context(self, updates: dict[str, Any]) -> None:
        self.context.update(updates)

    def curry(self, **kwargs: Any) -> Callable[[Context], Context]:
        """Return a callable that overlays preset values before execution."""

        preset = {**self.context, **kwargs}

        def curried(context: Context) -> Context:
            context.update(preset)
            return self(context)

        return curried

    def bind(self, func: Callable[[Any], Any]) -> "ValueVerb":
        """Transform a previously produced ``value`` while preserving context."""

        if not hasattr(self, "value"):
            raise VerbExecutionError("bind requires the verb to expose a 'value' attribute")
        return ValueVerb(func(getattr(self, "value")), context=self.context)


class ValueVerb(DSLVerb):
    """Concrete verb carrying a value through a composition chain."""

    def __init__(self, value: Any, context: Context | None = None) -> None:
        super().__init__(context=context)
        self.value = value

    def __call__(self, context: Context) -> Context:
        context["value"] = self.value
        return context


class ComposeVerb(DSLVerb):
    """Sequentially execute two verbs using the first result as the second input."""

    def __init__(self, verb1: DSLVerb, verb2: DSLVerb) -> None:
        super().__init__(context={**verb1.context, **verb2.context})
        self.verb1 = verb1
        self.verb2 = verb2

    def __call__(self, context: Context) -> Context:
        first = self.verb1(context)
        if first is None:  # defensive compatibility for third-party legacy verbs
            raise VerbExecutionError(f"{type(self.verb1).__name__} returned None")
        second = self.verb2(first)
        if second is None:
            raise VerbExecutionError(f"{type(self.verb2).__name__} returned None")
        return second


class FetchData(DSLVerb):
    """Fetch a JSON document over HTTP(S) into ``context['data']``."""

    def __init__(self, context: Context | None = None, *, timeout: float = 10.0, **kwargs: Any) -> None:
        super().__init__(context=context, **kwargs)
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self.timeout = timeout

    def __call__(self, context: Context) -> Context:
        url = context.get("url")
        if not isinstance(url, str) or not url.strip():
            raise VerbExecutionError("FetchData requires a non-empty 'url'")
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "dslmodel/verbs"})
        try:
            with urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - caller supplies URL by design
                charset = response.headers.get_content_charset() or "utf-8"
                payload = response.read().decode(charset)
        except (HTTPError, URLError, OSError, UnicodeError) as exc:
            raise VerbExecutionError(f"failed to fetch JSON from {url}: {exc}") from exc
        try:
            context["data"] = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise VerbExecutionError(f"response from {url} is not valid JSON") from exc
        return context


class ProcessData(DSLVerb):
    """Remove falsy values from JSON object fields while preserving structure."""

    @staticmethod
    def _filter_mapping(item: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in item.items() if value}

    def __call__(self, context: Context) -> Context:
        if "data" not in context:
            raise VerbExecutionError("ProcessData requires 'data' in context")
        data = context["data"]
        if isinstance(data, dict):
            processed: Any = self._filter_mapping(data)
        elif isinstance(data, list):
            if not all(isinstance(item, dict) for item in data):
                raise VerbExecutionError("ProcessData list inputs must contain only JSON objects")
            processed = [self._filter_mapping(item) for item in data]
        else:
            raise VerbExecutionError("ProcessData supports only JSON objects or lists of objects")
        context["processed_data"] = processed
        return context


class SaveToFile(DSLVerb):
    """Atomically persist ``processed_data`` as UTF-8 JSON."""

    def __call__(self, context: Context) -> Context:
        if "processed_data" not in context:
            raise VerbExecutionError("SaveToFile requires 'processed_data' in context")
        path = Path(context.get("file_path", "output.json"))
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path: Path | None = None
        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                json.dump(context["processed_data"], handle, indent=2, sort_keys=True)
                handle.write("\n")
                temp_path = Path(handle.name)
            temp_path.replace(path)
        except (OSError, TypeError, ValueError) as exc:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass
            raise VerbExecutionError(f"failed to save JSON to {path}: {exc}") from exc
        context["saved_file"] = str(path)
        return context
