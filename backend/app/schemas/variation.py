"""Schemas for the variations endpoint (Step 4: generate conceptual variations)."""

from uuid import uuid4

from pydantic import Field, field_validator

from .analysis import AnalysisResponse
from .common import QuestionText, StrictModel, VariationCategory


class VariationsRequest(StrictModel):
    """Request body for `POST /api/v1/problems/variations`.

    The client sends back the original question and its analysis, so the
    backend doesn't need to store anything between calls. Variations are
    generated using both as context.
    """

    question: str = QuestionText
    analysis: AnalysisResponse
    categories: list[VariationCategory] = Field(min_length=1)
    count_per_category: int = Field(default=1, ge=1, le=3)

    @field_validator("categories")
    @classmethod
    def categories_unique(cls, v: list[VariationCategory]) -> list[VariationCategory]:
        """Reject duplicate categories so counts stay predictable."""
        if len(set(v)) != len(v):
            raise ValueError("categories must not contain duplicates")
        return v


class Variation(StrictModel):
    """A new practice question that tests the same underlying concepts.

    Deliberately contains no answer. Students attempt the variation first,
    and the answer is only produced by the explain endpoint on request.
    """

    # Assigned by the backend, so the model's output doesn't need to include it.
    id: str = Field(default_factory=lambda: uuid4().hex)
    category: VariationCategory
    question: str = Field(min_length=1)
    modified_conditions: list[str] = Field(
        description="What was changed relative to the original problem"
    )
    learning_objective: str = Field(
        min_length=1, description="What concept this variation tests"
    )


class VariationsResponse(StrictModel):
    """Response body for the variations endpoint: the generated questions."""

    variations: list[Variation]

class VariationDraft(StrictModel):
    """A variation as produced by the AI, before the backend assigns an id."""

    category: VariationCategory
    question: str = Field(min_length=1)
    modified_conditions: list[str]
    learning_objective: str = Field(min_length=1)


class VariationDrafts(StrictModel):
    """Tool-output wrapper: the AI returns all variations in one object."""

    variations: list[VariationDraft]