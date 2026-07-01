"""
Input validation utilities.
All validation logic is centralised here — keeps route handlers clean.
"""

from fastapi import UploadFile, HTTPException
from app.config import config


# Allowed MIME types for resume uploads
ALLOWED_MIME_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}


def validate_resume_file(file: UploadFile) -> None:
    """
    Validates the uploaded resume file.

    Checks:
    - File is actually attached
    - File has a filename
    - File extension is .pdf
    - MIME type is application/pdf

    Raises:
        HTTPException 400: if any validation fails
    """
    # Check file exists
    if not file:
        raise HTTPException(
            status_code=400,
            detail="No file was uploaded. Please attach a PDF resume."
        )

    # Check filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file has no filename."
        )

    # Check file extension
    extension = "." + file.filename.rsplit(".", 1)[-1].lower() \
        if "." in file.filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{extension}'. Only PDF files are accepted."
        )

    # Check MIME type (content type sent by browser)
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid content type '{file.content_type}'. "
                "Please upload a valid PDF file."
            )
        )


def validate_file_size(file_bytes: bytes) -> None:
    """
    Validates that the file does not exceed the max allowed size.

    Args:
        file_bytes: Raw bytes of the uploaded file

    Raises:
        HTTPException 400: if file is empty or too large
    """
    size_mb = len(file_bytes) / (1024 * 1024)

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if size_mb > config.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File size {size_mb:.1f}MB exceeds the "
                f"{config.MAX_FILE_SIZE_MB}MB limit."
            )
        )


def validate_job_description(job_description: str) -> None:
    """
    Validates the job description text input.

    Checks:
    - Not empty or whitespace-only
    - Meets minimum length (too short = not useful for analysis)
    - Does not exceed maximum length (prevent abuse / token overflow)

    Raises:
        HTTPException 400: if any validation fails
    """
    jd = job_description.strip()

    if not jd:
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    if len(jd) < config.MIN_JD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Job description is too short ({len(jd)} characters). "
                f"Please provide at least {config.MIN_JD_LENGTH} characters "
                "for a meaningful analysis."
            )
        )

    if len(jd) > config.MAX_JD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Job description is too long ({len(jd)} characters). "
                f"Maximum allowed is {config.MAX_JD_LENGTH} characters."
            )
        )