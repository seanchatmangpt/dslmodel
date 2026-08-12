from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import pytest

from dslmodel.readers.doc_reader import DocReader, DocumentReadError, read_any, read_docx_file, extract_texts_from_epub


def test_text_reader_and_chunks(tmp_path: Path) -> None:
    source = tmp_path / "note.MD"
    source.write_text("hello\n\nworld", encoding="utf-8")
    assert read_any(source) == "hello world"
    reader = DocReader(source)
    assert reader.forward() == "hello world"
    assert reader.read_chunks(5) == ["hello", " worl", "d"]
    with pytest.raises(ValueError, match="greater than zero"):
        reader.read_chunks(0)


def test_docx_reader_extracts_paragraphs(tmp_path: Path) -> None:
    source = tmp_path / "document.docx"
    document_xml = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Hello</w:t></w:r><w:r><w:t> world</w:t></w:r></w:p>
    <w:p><w:r><w:t>Second paragraph</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
    with ZipFile(source, "w") as archive:
        archive.writestr("word/document.xml", document_xml)
    assert read_docx_file(source) == "Hello world Second paragraph"


def test_epub_reader_respects_spine_order(tmp_path: Path) -> None:
    source = tmp_path / "book.epub"
    container_xml = """<?xml version="1.0"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
    package_xml = """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <manifest>
    <item id="one" href="one.xhtml" media-type="application/xhtml+xml"/>
    <item id="two" href="two.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine><itemref idref="two"/><itemref idref="one"/></spine>
</package>
"""
    with ZipFile(source, "w") as archive:
        archive.writestr("META-INF/container.xml", container_xml)
        archive.writestr("OEBPS/content.opf", package_xml)
        archive.writestr("OEBPS/one.xhtml", "<html><body><p>First</p><script>ignore me</script></body></html>")
        archive.writestr("OEBPS/two.xhtml", "<html><body><p>Second</p></body></html>")
    assert extract_texts_from_epub(source) == "Second First"


def test_invalid_archives_fail_with_typed_error(tmp_path: Path) -> None:
    source = tmp_path / "bad.docx"
    source.write_text("not a zip", encoding="utf-8")
    with pytest.raises(DocumentReadError):
        read_docx_file(source)


def test_supported_extensions_are_case_insensitive() -> None:
    assert DocReader.supports_file_type("PDF")
    assert DocReader.supports_file_type(".docx")
    assert not DocReader.supports_file_type(".xlsx")
