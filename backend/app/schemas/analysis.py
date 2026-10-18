"""Schemas for the analyze endpoint (Step 3: identify the underlying concepts)."""

from pydantic import Field

from .common import QuestionText, StrictModel


class AnalyzeRequest(StrictModel):
    """Request body for `POST /api/v1/problems/analyze`.

    Contains only the question text captured by the extension (from the
    selected text or the page).
    """
    question: str = QuestionText


class AnalysisResponse(StrictModel):
    """Conceptual breakdown of a question.

    Explains why the problem works the way it does, split into the principles
    being tested, the assumptions behind the reasoning, and the constraints on
    valid methods or answers. This object is also sent back by the client when
    requesting variations, so the backend can stay stateless.
    """
    
    summary: str = Field(min_length=1, description="One or two sentences on what the problem asks")
    principles: list[str] = Field(
        min_length=1, description="Fundamental rules or ideas being tested"
    )
    assumptions: list[str] = Field(
        description="What must be true for the reasoning to work"
    )
    constraints: list[str] = Field(
        description="Conditions that limit which methods or answers are valid"
    )
    reasoning: str = Field(
        min_length=1, description="Why these concepts apply to this problem"
    )