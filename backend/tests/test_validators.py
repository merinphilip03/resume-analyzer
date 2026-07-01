"""
Basic tests for input validators.
Tests run in CI without needing a real API key.
"""

import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from app.utils.validators import (
    validate_file_size,
    validate_job_description,
    validate_resume_file
)


# ── File size tests ──────────────────────────────────────

def test_valid_file_size():
    """A normal size file should pass without error."""
    fake_bytes = b"x" * (1 * 1024 * 1024)  # 1MB
    validate_file_size(fake_bytes)           # should not raise


def test_empty_file_raises():
    """An empty file should raise a 400 error."""
    with pytest.raises(HTTPException) as exc:
        validate_file_size(b"")
    assert exc.value.status_code == 400


def test_oversized_file_raises():
    """A file over 5MB should raise a 400 error."""
    big_file = b"x" * (6 * 1024 * 1024)  # 6MB
    with pytest.raises(HTTPException) as exc:
        validate_file_size(big_file)
    assert exc.value.status_code == 400


# ── Job description tests ────────────────────────────────

def test_valid_job_description():
    """A normal job description should pass."""
    jd = "We are looking for a Python developer " * 5
    validate_job_description(jd)  # should not raise


def test_empty_job_description_raises():
    """Empty job description should raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_job_description("")
    assert exc.value.status_code == 400


def test_whitespace_only_raises():
    """Whitespace-only job description should raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_job_description("     ")
    assert exc.value.status_code == 400


def test_too_short_raises():
    """Job description under 50 chars should raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_job_description("too short")
    assert exc.value.status_code == 400


def test_too_long_raises():
    """Job description over 5000 chars should raise 400."""
    with pytest.raises(HTTPException) as exc:
        validate_job_description("x" * 5001)
    assert exc.value.status_code == 400


# ── File type tests ──────────────────────────────────────

def test_valid_pdf_file():
    """A proper PDF file should pass validation."""
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.content_type = "application/pdf"
    validate_resume_file(mock_file)  # should not raise


def test_non_pdf_extension_raises():
    """A .docx file should raise 400."""
    mock_file = MagicMock()
    mock_file.filename = "resume.docx"
    mock_file.content_type = "application/pdf"
    with pytest.raises(HTTPException) as exc:
        validate_resume_file(mock_file)
    assert exc.value.status_code == 400


def test_wrong_mime_type_raises():
    """A renamed .exe file should raise 400."""
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.content_type = "application/octet-stream"
    with pytest.raises(HTTPException) as exc:
        validate_resume_file(mock_file)
    assert exc.value.status_code == 400