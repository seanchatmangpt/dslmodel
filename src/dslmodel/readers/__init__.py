"""Dependency-closed document reader API."""

from .doc_reader import (
    DocReader,
    DocumentReadError,
    ReaderDependencyError,
    clean_text,
    extract_texts_from_epub,
    read_any,
    read_docx_file,
    read_text_file,
    read_text_from_pdf,
)

__all__ = [
    "DocReader",
    "DocumentReadError",
    "ReaderDependencyError",
    "clean_text",
    "extract_texts_from_epub",
    "read_any",
    "read_docx_file",
    "read_text_file",
    "read_text_from_pdf",
]
