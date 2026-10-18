"""Routes for the core learning flow: analyze, generate variations, explain."""

from fastapi import APIRouter

from app.config import settings
from app.schemas import (
    AnalysisResponse,
    AnalyzeRequest,
    ExplainRequest,
    ExplainResponse,
    VariationsRequest,
    VariationsResponse,
)
from app.services import ai_service, mock_data

router = APIRouter(prefix="/api/v1/problems", tags=["problems"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(req: AnalyzeRequest) -> AnalysisResponse:
    """Break a question into principles, assumptions, constraints, and reasoning."""
    if settings.use_mock:
        return mock_data.get_analysis(req.question)
    return ai_service.analyze(req.question)


@router.post("/variations", response_model=VariationsResponse)
def variations(req: VariationsRequest) -> VariationsResponse:
    """Generate conceptual variations for the requested categories."""
    if settings.use_mock:
        items = mock_data.get_variations(req.question, req.categories)
    else:
        items = ai_service.variations(
            req.question, req.analysis, req.categories, req.count_per_category
        )
    return VariationsResponse(variations=items)


@router.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest) -> ExplainResponse:
    """Reveal the answer and explanation for a single variation."""
    if settings.use_mock:
        return mock_data.get_explanation(req.variation)
    return ai_service.explain(req.question, req.variation)