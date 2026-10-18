from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base model that rejects unknown fields. Useful for validating AI output."""

    model_config = ConfigDict(extra="forbid")


class VariationCategory(str, Enum):
    CHANGED_CONDITIONS = "changed_conditions"
    EDGE_CASES = "edge_cases"
    NEGATION_COUNTEREXAMPLE = "negation_counterexample"
    REVERSE_REASONING = "reverse_reasoning"


# Shared constraint so a huge paste can't blow up prompts or cost.
QuestionText = Field(min_length=1, max_length=5000)


class ErrorResponse(StrictModel):
    code: str = Field(description="Machine-readable error code, e.g. 'ai_invalid_output'")
    message: str = Field(description="Human-readable message safe to show the student")
    retryable: bool = Field(description="Whether the client should offer a retry")