"""
LLM Service — LangChain + Gemini chain for resume analysis.
Now includes project ideas, tailored resume, and ATS breakdown.
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
    Chain: PromptTemplate → Gemini LLM → JsonOutputParser
    """

    llm = ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=0.3,
        max_retries=2,
    )

    parser = JsonOutputParser(pydantic_object=ResumeAnalysisResponse)

    prompt = PromptTemplate(
        template="""
You are an expert ATS resume screener, career coach, and technical recruiter
with deep knowledge of what makes resumes pass ATS systems.

Analyze the resume against the job description and return a comprehensive
evaluation with actionable improvements.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

INSTRUCTIONS:

1. MATCH ANALYSIS
   - Calculate a realistic ATS match score (0-100)
   - Identify specific strengths (exact skills/experience that match)
   - Identify missing keywords (skills in JD not found in resume)
   - Write a 2-3 sentence honest summary
   - Give one specific, actionable improvement tip

2. PROJECT IDEAS (generate exactly 2-3 ideas)
   - Each project must address one or more identified skill gaps.
   - Build on the candidate's existing skills while incorporating 1-3 relevant technologies or concepts required by the target job that the candidate lacks.
   - Projects should be realistic for the candidate to complete independently, while providing meaningful exposure to new tools, frameworks, or industry practices.
   - Prefer real-world, portfolio-worthy projects over basic CRUD or tutorial projects.
   - Each project must have: title, description, tech_stack (list), impact
   
   
3. TAILORED RESUME
   - Rewrite the resume content to be ATS-optimized for this specific job
   - Naturally incorporate missing keywords where the candidate has relevant experience
   - Do NOT fabricate experience or skills they don't have
   - Strengthen weak bullet points with more specific language
   - Use action verbs and quantify achievements where possible
   - Return as plain text with clear sections (SUMMARY, EXPERIENCE, SKILLS, etc.)
   - Keep it honest — only enhance what's already there

4. ATS CRITERIA BREAKDOWN (check all of these)
   - Keyword match: does resume contain the main technical keywords from JD?
   - Quantified achievements: does resume have numbers/metrics in bullets?
   - Action verbs: does resume start bullets with strong action verbs?
   - Relevant section headers: does resume have standard sections (Experience, Skills, Education)?
   - Skills section: is there a dedicated skills/technologies section?
   - Job title alignment: does candidate's experience align with the role level?
   Each criterion must have: criterion (string), passed (boolean), note (string explanation)

{format_instructions}

IMPORTANT:
- Base ALL analysis on what is actually written in the resume
- Do not fabricate skills or experience
- tech_stack in project_ideas must always be a JSON array of strings
- tailored_resume must be a plain text string (not JSON, not markdown)
""",
        input_variables=["resume_text", "job_description"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    return prompt | llm | parser


# Build chain once at module load
_chain = _build_chain()


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Runs the full resume analysis chain and returns structured results.

    Args:
        resume_text:     Extracted plain text from the resume PDF
        job_description: Raw job description text from the user

    Returns:
        Dictionary matching ResumeAnalysisResponse schema

    Raises:
        HTTPException 422: if LLM returns malformed output
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

        # Validate result matches our schema
        validated = ResumeAnalysisResponse(**result)
        logger.info(
            "Analysis complete. Score: %d, Projects: %d, ATS criteria: %d",
            validated.match_score,
            len(validated.project_ideas),
            len(validated.ats_criteria)
        )
        return validated.model_dump()

    except (OutputParserException, ValidationError, KeyError) as e:
        logger.error("LLM output parsing failed: %s", str(e))
        raise HTTPException(
            status_code=422,
            detail="The AI returned an unexpected response. Please try again."
        )

    except HTTPException:
        raise

    except Exception as e:
        error_str = str(e).lower()

        if "429" in error_str or "resource_exhausted" in error_str or "quota" in error_str:
            logger.warning("Gemini rate limit hit: %s", str(e))
            raise HTTPException(
                status_code=429,
                detail="AI rate limit reached. Please wait a moment and try again."
            )

        if "503" in error_str or "unavailable" in error_str or "connection" in error_str:
            logger.error("Gemini API unreachable: %s", str(e))
            raise HTTPException(
                status_code=503,
                detail="AI service temporarily unavailable. Please try again."
            )

        logger.error("Unexpected LLM error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during analysis."
        )