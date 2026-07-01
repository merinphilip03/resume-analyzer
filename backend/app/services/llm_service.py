"""
LLM Service — LangChain + Gemini chain for resume analysis.
All AI/LLM logic is isolated here. Swapping the LLM provider
only requires changes in this one file.
"""

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from fastapi import HTTPException
from pydantic import ValidationError

from app.config import config
from app.models import ResumeAnalysisResponse

logger = logging.getLogger(__name__)


def _build_chain():
    """
    Builds and returns the LangChain LCEL chain.

    Chain structure:
        PromptTemplate → Gemini LLM → JsonOutputParser

    Returns:
        A runnable LangChain chain
    """
    # 1. LLM — Gemini via LangChain
    llm = ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=0.3,      # Lower = more consistent/factual output
        max_retries=2,        # Auto-retry on transient API errors
    )

    # 2. Output parser — enforces JSON structure
    parser = JsonOutputParser(pydantic_object=ResumeAnalysisResponse)

    # 3. Prompt template — clear instructions + output format
    prompt = PromptTemplate(
        template="""
You are an expert ATS (Applicant Tracking System) resume screener and career coach.

Your task is to analyze how well the candidate's resume matches the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

INSTRUCTIONS:
- Be specific and practical in your analysis
- Base your analysis ONLY on what is actually written in the resume
- Do not make assumptions about skills not mentioned
- The match_score should reflect realistic ATS compatibility (0-100)
- missing_keywords should list specific skills/tools from the JD not found in the resume
- strengths should list specific matches you found between the resume and JD
- improvement_tip should be ONE concrete, actionable suggestion

{format_instructions}
""",
        input_variables=["resume_text", "job_description"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    # 4. LCEL chain — pipe operator connects components
    return prompt | llm | parser


# Build chain once at module load (not on every request)
_chain = _build_chain()


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Runs the resume analysis chain and returns structured results.

    Args:
        resume_text:      Extracted plain text from the resume PDF
        job_description:  Raw job description text from the user

    Returns:
        Dictionary matching ResumeAnalysisResponse schema

    Raises:
        HTTPException 422: if LLM returns malformed/unparseable output
        HTTPException 429: if Gemini API rate limit is exceeded
        HTTPException 503: if Gemini API is unreachable
        HTTPException 500: for any other unexpected errors
    """
    try:
        logger.info("Starting resume analysis via Gemini...")

        result = _chain.invoke({
            "resume_text": resume_text,
            "job_description": job_description
        })

        # Validate the result matches our expected schema
        validated = ResumeAnalysisResponse(**result)
        logger.info(
            "Analysis complete. Match score: %d", validated.match_score
        )
        return validated.model_dump()

    except (OutputParserException, ValidationError, KeyError) as e:
        # LLM returned something we couldn't parse into our schema
        logger.error("LLM output parsing failed: %s", str(e))
        raise HTTPException(
            status_code=422,
            detail=(
                "The AI returned an unexpected response format. "
                "Please try again."
            )
        )

    except HTTPException:
        raise

    except Exception as e:
        error_str = str(e).lower()

        # Rate limit errors from Gemini API
        if "429" in error_str or "resource_exhausted" in error_str or "quota" in error_str:
            logger.warning("Gemini API rate limit hit: %s", str(e))
            raise HTTPException(
                status_code=429,
                detail=(
                    "AI service rate limit reached. "
                    "Please wait a moment and try again."
                )
            )

        # Network/connectivity errors
        if "503" in error_str or "unavailable" in error_str or "connection" in error_str:
            logger.error("Gemini API unreachable: %s", str(e))
            raise HTTPException(
                status_code=503,
                detail=(
                    "AI service is temporarily unavailable. "
                    "Please try again in a few seconds."
                )
            )

        # Catch-all for anything else
        logger.error("Unexpected LLM error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during analysis."
        )