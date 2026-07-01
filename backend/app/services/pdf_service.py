"""
PDF Service — handles all PDF text extraction logic.
Isolated here so the route handler stays clean and this can be
swapped out independently (e.g. switch from PyPDF2 to pdfminer).
"""

import io
import logging
import PyPDF2
from fastapi import HTTPException
from app.config import config

# Module-level logger
logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts plain text from a PDF file given its raw bytes.

    Handles:
    - Normal text-based PDFs
    - Multi-page PDFs (concatenates all pages)
    - Partially readable PDFs (skips unreadable pages with a warning)
    - Encrypted PDFs (raises a user-friendly error)
    - Scanned/image-only PDFs (detects empty extraction and raises error)

    Args:
        file_bytes: Raw bytes of the uploaded PDF

    Returns:
        Extracted text as a single string

    Raises:
        HTTPException 400: if PDF is encrypted, unreadable, or image-only
        HTTPException 500: if an unexpected error occurs during extraction
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))

        # Edge case: encrypted PDF
        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded PDF is password-protected. "
                    "Please upload an unencrypted PDF."
                )
            )

        # Edge case: PDF has no pages
        if len(reader.pages) == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF has no pages."
            )

        extracted_pages = []
        skipped_pages = 0

        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text and text.strip():
                    extracted_pages.append(text.strip())
                else:
                    # Page exists but no text could be extracted
                    skipped_pages += 1
                    logger.warning(
                        "No text extracted from page %d", page_num + 1
                    )
            except Exception as page_error:
                # Skip problematic pages but continue with rest
                skipped_pages += 1
                logger.warning(
                    "Could not read page %d: %s", page_num + 1, str(page_error)
                )

        full_text = "\n\n".join(extracted_pages).strip()

        # Edge case: all pages were skipped (likely a scanned/image PDF)
        if not full_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract any text from the PDF. "
                    "This usually means it is a scanned image PDF. "
                    "Please upload a text-based PDF resume."
                )
            )

        # Edge case: extracted text is suspiciously short
        if len(full_text) < config.MIN_RESUME_TEXT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Extracted text is too short ({len(full_text)} characters). "
                    "The PDF may be mostly images or corrupted. "
                    "Please upload a text-based PDF resume."
                )
            )

        if skipped_pages > 0:
            logger.info(
                "PDF processed with %d skipped pages out of %d total.",
                skipped_pages,
                len(reader.pages)
            )

        logger.info(
            "Successfully extracted %d characters from %d pages.",
            len(full_text),
            len(reader.pages)
        )

        return full_text

    except HTTPException:
        # Re-raise our own HTTP errors as-is
        raise

    except PyPDF2.errors.PdfReadError as e:
        logger.error("PyPDF2 could not read the file: %s", str(e))
        raise HTTPException(
            status_code=400,
            detail=(
                "The file appears to be corrupted or is not a valid PDF. "
                "Please try uploading a different file."
            )
        )

    except Exception as e:
        logger.error("Unexpected error during PDF extraction: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while reading the PDF."
        )