"""
Analyze router — handles the /analyze API endpoint.
Route handler is kept thin: validate → extract → analyze → respond.
All heavy logic lives in services.
"""

import logging
from fastapi import APIRouter, UploadFile, File, Form

from app.models import ResumeAnalysisResponse
from app.services.pdf_service import extract_text_from_pdf
from app.services.llm_service import analyze_resume
from app.utils.validators import (
    validate_resume_file,
    validate_file_size,
    validate_job_description,
)

logger = logging.getLogger(__name__)

# Create router with prefix and tag for auto-docs grouping
router = APIRouter(prefix="/api/v1", tags=["Resume Analysis"])


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResponse,
    summary="Analyze resume against a job description",
    description=(
        "Upload a PDF resume and provide a job description. "
        "Returns an ATS match score, strengths, missing keywords, "
        "and an actionable improvement tip."
    )
)
async def analyze_endpoint(
    resume: UploadFile = File(..., description="Resume in PDF format (max 5MB)"),
    job_description: str = Form(..., description="Full job description text")
):
    """
    POST /api/v1/analyze

    Steps:
    1. Validate file metadata (type, extension)
    2. Read file bytes and validate size
    3. Validate job description text
    4. Extract text from PDF
    5. Run LLM analysis chain
    6. Return structured response
    """

    # Step 1: Validate file metadata before reading bytes
    validate_resume_file(resume)

    # Step 2: Read file bytes and validate size
    file_bytes = await resume.read()
    validate_file_size(file_bytes)

    # Step 3: Validate job description
    validate_job_description(job_description)

    # Step 4: Extract text from PDF
    logger.info("Extracting text from: %s", resume.filename)
    resume_text = extract_text_from_pdf(file_bytes)

    # Step 5: Run LLM analysis
    result = analyze_resume(resume_text, job_description)

    # Step 6: Return result (auto-serialized by FastAPI)
    return result