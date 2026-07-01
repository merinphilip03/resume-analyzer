"""
FastAPI application factory.
Configures the app, middleware, routers, and startup checks.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.routers.analyze import router as analyze_router

# Configure logging for the whole app
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Application factory — creates and configures the FastAPI app.
    Using a factory function makes the app easier to test.
    """

    # Validate config at startup — fail fast if API key is missing
    config.validate()

    app = FastAPI(
        title="AI Resume Analyzer",
        description="Analyze resume-job description match using Gemini + LangChain",
        version="1.0.0",
    )

    # CORS middleware — allows React frontend to call this API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],      # Tighten this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(analyze_router)

    # Health check endpoint — useful for Render deployment checks
    @app.get("/", tags=["Health"])
    def health_check():
        """Returns API status. Used by deployment platforms to verify the app is running."""
        return {
            "status": "ok",
            "service": "AI Resume Analyzer API",
            "version": "1.0.0"
        }

    logger.info("App created successfully. Model: %s", config.GEMINI_MODEL)
    return app


# Create the app instance
app = create_app()