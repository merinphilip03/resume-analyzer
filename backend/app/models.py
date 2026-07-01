"""
Pydantic models for API request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import List


class ResumeAnalysisResponse(BaseModel):
    """
    Structured response returned to the frontend after analysis.
    All fields are required — LLM is prompted to always return these.
    """

    match_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="ATS match score from 0 to 100"
    )
    summary: str = Field(
        ...,
        description="2-4 sentence overall assessment"
    )
    strengths: List[str] = Field(
        ...,
        min_length=1,
        description="Skills/experience that match the job well"
    )
    missing_keywords: List[str] = Field(
        ...,
        description="Important skills/keywords missing from the resume"
    )
    improvement_tip: str = Field(
        ...,
        description="One specific, actionable improvement suggestion"
    )


class ErrorResponse(BaseModel):
    """Standard error response shape."""

    error: str
    detail: str = ""