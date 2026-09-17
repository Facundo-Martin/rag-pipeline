"""Unit tests for the Docling infrastructure gateway."""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.docling.parser import DoclingGateway
from src.infrastructure.docling.schemas import ParsedDocument


@patch("src.infrastructure.docling.parser.DocumentConverter")
def test_parse_pdf_success(mock_converter_class, tmp_path):
    """Ensures the gateway correctly executes the pipeline and maps to the DTO."""
    mock_instance = MagicMock()
    mock_converter_class.return_value = mock_instance

    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "# Fake Paper\nTable 1."
    mock_instance.convert.return_value = mock_result

    fake_pdf = tmp_path / "test.pdf"
    fake_pdf.write_text("dummy pdf bytes")

    gateway = DoclingGateway(enable_ocr=False)
    result = gateway.parse_pdf(fake_pdf)

    assert isinstance(result, ParsedDocument)
    assert result.markdown_content == "# Fake Paper\nTable 1."
    assert result.char_count == 21
    assert result.elapsed_seconds >= 0.0


def test_parse_pdf_file_not_found(caplog: pytest.LogCaptureFixture):
    """Ensures the gateway traps missing files before hitting the heavy ML models."""
    gateway = DoclingGateway(enable_ocr=False)

    # The gateway intentionally logs the missing file; keep that expected error out of the output.
    with (
        caplog.at_level(logging.CRITICAL, logger="src.infrastructure.docling.parser"),
        pytest.raises(FileNotFoundError),
    ):
        gateway.parse_pdf(Path("/tmp/does_not_exist.pdf"))
