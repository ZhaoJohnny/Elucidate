from uuid import uuid4

from pydantic import Field, field_validator

from .analysis import AnalysisResponse
from .common import QuestionText, StrictModel, VariationCategory


class VariationsRequest(StrictModel):
    question: str = QuestionText
    analysis: AnalysisResponse
    categories: list[VariationCategory] = Field(min_length=1)
    count_per_category: int = Field(default=1, ge=1, le=3)

    @field_validator("categories")
    @classmethod
    def categories_unique(cls, v: list[VariationCategory]) -> list[VariationCategory]:
        if len(set(v)) != len(v):
            raise ValueError("categories must not contain duplicates")
        return v


class Variation(StrictModel):
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
    # The answer is deliberately NOT here. It's only generated via /explain,
    # so students attempt the problem before it can be revealed.


class VariationsResponse(StrictModel):
    variations: list[Variation]