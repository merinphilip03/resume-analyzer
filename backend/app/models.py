"""
Pydantic models for API request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import List


class ProjectIdea(BaseModel):
    """A single portfolio project idea."""
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="What to build and why it fills the gap")
    tech_stack: List[str] = Field(..., description="Technologies to use")
    impact: str = Field(..., description="How this project improves ATS match")


class ATSCriteria(BaseModel):
    """Individual ATS check result."""
    criterion: str = Field(..., description="What was checked")
    passed: bool = Field(..., description="Whether it passed")
    note: str = Field(..., description="Explanation")


class ResumeAnalysisResponse(BaseModel):
    """
    Full structured response returned to the frontend after analysis.
    """

    # Existing fields
    match_score: int = Field(..., ge=0, le=100, description="ATS match score 0-100")
    summary: str = Field(..., description="2-3 sentence overall assessment")
    strengths: List[str] = Field(..., description="Skills that match the job well")
    missing_keywords: List[str] = Field(..., description="Important missing skills")
    improvement_tip: str = Field(..., description="One specific actionable tip")

    # New fields
    project_ideas: List[ProjectIdea] = Field(
        ..., description="2-3 portfolio project ideas to fill skill gaps"
    )
    tailored_resume: str = Field(
        ..., description="ATS-optimized rewritten resume content"
    )
    ats_criteria: List[ATSCriteria] = Field(
        ..., description="Breakdown of ATS pass/fail criteria"
    )


class ErrorResponse(BaseModel):
    """Standard error response shape."""
    error: str
    detail: str = ""