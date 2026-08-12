"""Dependency-light document text readers.

TXT/Markdown, DOCX, and EPUB are handled with the Python standard library.
PDF extraction uses the optional ``pypdf`` backend and fails closed with a
clear dependency error when it is unavailable.
"""

from __future__ import annotations

from html.parser import HTMLParser
import importlib
from pathlib import Path, PurePosixPath
import re
from typing import Any
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

try:  # Preserve the legacy DSPy Retrieve interface when DSPy is installed.
    import dspy
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal installs
    class _Retrieve:
        def __init__(self, *_: Any, **__: Any) -> None:
            super().__init__()
else:
    _Retrieve = dspy.Retrieve


class DocumentReadError(ValueError):
    """Raised when a document cannot be safely decoded or extracted."""


class ReaderDependencyError(DocumentReadError):
    """Raised when an explicitly requested optional reader backend is absent."""


_WHITESPACE = re.compile(r"\s+")
_MAX_PDF_CONTENT_STREAM_BYTES = 64 * 1024 * 1024


def clean_text(text: str) -> str:
    """Normalize non-breaking and repeated whitespace without changing words."""

    return _WHITESPACE.sub(" ", text.replace("\xa0", " ")).strip()


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag.lower() in {"script", "style"}:
            self._ignored_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self._parts.append(data)

    def text(self) -> str:
        return clean_text(" ".join(self._parts))


def _html_text(payload: bytes) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(payload.decode("utf-8", errors="replace"))
    parser.close()
    return parser.text()


def extract_texts_from_epub(file_name: str | Path) -> str:
    """Extract EPUB chapters in spine order using ZIP/XML metadata."""

    path = Path(file_name)
    try:
        with ZipFile(path) as archive:
            try:
                container = ET.fromstring(archive.read("META-INF/container.xml"))
                rootfile = next(
                    node.attrib["full-path"]
                    for node in container.iter()
                    if node.tag.rsplit("}", 1)[-1] == "rootfile" and node.attrib.get("full-path")
                )
                package = ET.fromstring(archive.read(rootfile))
            except (KeyError, StopIteration, ET.ParseError) as exc:
                raise DocumentReadError(f"invalid EPUB package metadata: {path}") from exc

            manifest: dict[str, str] = {}
            spine: list[str] = []
            for node in package.iter():
                local = node.tag.rsplit("}", 1)[-1]
                if local == "item" and node.attrib.get("id") and node.attrib.get("href"):
                    media_type = node.attrib.get("media-type", "")
                    if media_type in {"application/xhtml+xml", "text/html"}:
                        manifest[node.attrib["id"]] = node.attrib["href"]
                elif local == "itemref" and node.attrib.get("idref"):
                    spine.append(node.attrib["idref"])

            package_dir = PurePosixPath(rootfile).parent
            chapter_paths = [package_dir / manifest[item_id] for item_id in spine if item_id in manifest]
            if not chapter_paths:
                chapter_paths = [package_dir / href for href in manifest.values()]
            if not chapter_paths:
                raise DocumentReadError(f"EPUB contains no readable document items: {path}")

            chapters: list[str] = []
            for chapter_path in chapter_paths:
                normalized = str(PurePosixPath(chapter_path))
                try:
                    text = _html_text(archive.read(normalized))
                except KeyError as exc:
                    raise DocumentReadError(f"EPUB manifest references missing item: {normalized}") from exc
                if text:
                    chapters.append(text)
    except (OSError, BadZipFile) as exc:
        raise DocumentReadError(f"cannot read EPUB {path}: {exc}") from exc

    return clean_text("\n\n".join(chapters))


def read_text_from_pdf(file_path: str | Path) -> str:
    """Extract selectable PDF text through the optional pypdf backend."""

    try:
        pypdf = importlib.import_module("pypdf")
    except ModuleNotFoundError as exc:
        raise ReaderDependencyError(
            "PDF extraction requires the optional reader dependency; install 'dslmodel[readers]'"
        ) from exc

    try:
        reader = pypdf.PdfReader(Path(file_path))
        pages: list[str] = []
        for index, page in enumerate(reader.pages):
            contents = page.get_contents()
            if contents is not None:
                raw = contents.get_data()
                if len(raw) > _MAX_PDF_CONTENT_STREAM_BYTES:
                    raise DocumentReadError(
                        f"PDF page {index + 1} content stream exceeds "
                        f"{_MAX_PDF_CONTENT_STREAM_BYTES} bytes"
                    )
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)
    except DocumentReadError:
        raise
    except Exception as exc:
        raise DocumentReadError(f"cannot extract PDF {file_path}: {exc}") from exc
    return clean_text("\n\n".join(pages))


def read_text_file(file_path: str | Path) -> str:
    """Read UTF-8 plaintext and normalize whitespace."""

    try:
        return clean_text(Path(file_path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise DocumentReadError(f"cannot read text file {file_path}: {exc}") from exc


def read_docx_file(file_path: str | Path) -> str:
    """Extract paragraphs from the OOXML document body without python-docx."""

    path = Path(file_path)
    try:
        with ZipFile(path) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))
    except (OSError, BadZipFile, KeyError, ET.ParseError) as exc:
        raise DocumentReadError(f"cannot read DOCX {path}: {exc}") from exc

    paragraphs: list[str] = []
    for paragraph in (node for node in document.iter() if node.tag.rsplit("}", 1)[-1] == "p"):
        parts: list[str] = []
        for node in paragraph.iter():
            local = node.tag.rsplit("}", 1)[-1]
            if local == "t" and node.text:
                parts.append(node.text)
            elif local == "tab":
                parts.append("\t")
            elif local in {"br", "cr"}:
                parts.append("\n")
        text = clean_text("".join(parts))
        if text:
            paragraphs.append(text)
    return clean_text("\n\n".join(paragraphs))


def read_any(file_path: str | Path) -> str:
    """Read a supported document based on its case-insensitive suffix."""

    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".epub":
        return extract_texts_from_epub(path)
    if suffix == ".pdf":
        return read_text_from_pdf(path)
    if suffix in {".txt", ".md"}:
        return read_text_file(path)
    if suffix == ".docx":
        return read_docx_file(path)
    return read_text_file(path)


class DocReader(_Retrieve):
    """Read a local document as text or deterministic fixed-size character chunks."""

    supported_extensions = [".epub", ".pdf", ".txt", ".md", ".docx"]

    def __init__(self, path: str | Path, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.path = Path(path)

    @classmethod
    def supports_file_type(cls, file_extension: str) -> bool:
        extension = file_extension if file_extension.startswith(".") else f".{file_extension}"
        return extension.lower() in cls.supported_extensions

    def read_chunks(self, chunk_chars: int) -> list[str]:
        if chunk_chars <= 0:
            raise ValueError("chunk_chars must be greater than zero")
        text = read_any(self.path)
        return [text[i : i + chunk_chars] for i in range(0, len(text), chunk_chars)]

    def forward(self, chunk_chars: int | None = None, **kwargs: Any) -> str | list[str]:
        del kwargs
        if chunk_chars is not None:
            return self.read_chunks(chunk_chars)
        return read_any(self.path)
