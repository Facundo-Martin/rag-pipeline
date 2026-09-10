"""Infrastructure gateway for the Docling PDF parser."""

import time
from pathlib import Path

import structlog
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption

from .schemas import ParsedDocument

logger = structlog.get_logger(__name__)


class DoclingParserError(Exception):
    """Domain exception for Docling deep-learning pipeline failures."""


class DoclingGateway:
    """
    An outbound adapter wrapping the Docling Vision-Language models.
    Configured specifically for high-accuracy scientific table extraction.
    """

    def __init__(self, enable_ocr: bool = True):
        """
        Initializes the Docling Converter with accurate table modeling.

        Args:
            enable_ocr: Whether to run OCR on embedded images/scanned pages.
                        Helpful for older ArXiv papers, but adds execution time.
        """
        logger.debug("initializing_docling_gateway", enable_ocr=enable_ocr)

        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_table_structure = True
        # ACCURATE mode prevents complex scientific tables from merging columns
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        pipeline_options.do_ocr = enable_ocr

        self.converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)},
        )

    def parse_pdf(self, pdf_path: Path | str) -> ParsedDocument:
        """
        Parses a PDF file from disk and returns a structured DTO.

        Args:
            pdf_path: The local file path to the downloaded PDF.

        Returns:
            A ParsedDocument DTO containing the markdown and timing metadata.

        Raises:
            FileNotFoundError: If the target PDF does not exist on disk.
            DoclingParserError: If the models fail to process the file (e.g., corrupt PDF).
        """
        path = Path(pdf_path)

        if not path.exists() or not path.is_file():
            logger.error("docling_file_not_found", path=str(path))
            raise FileNotFoundError(f"PDF file not found at: {path}")

        log = logger.bind(file_path=str(path), file_size_bytes=path.stat().st_size)
        log.info("docling_parsing_started")

        start_time = time.perf_counter()

        try:
            conversion_result = self.converter.convert(path)
            markdown_content = conversion_result.document.export_to_markdown()

            elapsed = round(time.perf_counter() - start_time, 2)
            char_count = len(markdown_content)

            log.info("docling_parsing_success", elapsed_seconds=elapsed, chars=char_count)

            return ParsedDocument(
                markdown_content=markdown_content, char_count=char_count, elapsed_seconds=elapsed
            )

        except Exception as e:
            elapsed = round(time.perf_counter() - start_time, 2)
            log.exception("docling_parsing_failed", elapsed_seconds=elapsed, error=str(e))
            raise DoclingParserError(f"Docling failed to parse PDF: {e!s}") from e


if __name__ == "__main__":
    import ssl
    import tempfile
    import urllib.request

    # Bypass macOS standard library SSL verification for this specific test
    ssl._create_default_https_context = ssl._create_unverified_context

    test_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        # Ignore Bandit B310: URL is hardcoded and safe for local testing
        urllib.request.urlretrieve(test_url, tmp.name)  # nosec B310
        print(f"Testing Docling against {tmp.name}...")

        gateway = DoclingGateway(enable_ocr=False)
        result = gateway.parse_pdf(tmp.name)

        print(f"Success! Extracted {result.char_count} characters in {result.elapsed_seconds}s")
