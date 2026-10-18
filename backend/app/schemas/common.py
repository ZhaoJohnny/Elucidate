"""Shared building blocks used across all request and response schemas."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base model that rejects unknown fields. Useful for validating AI output.
    
    Rejects unknown fields (`extra="forbid"`), which is especially useful when
    validating AI output: if the model invents or misnames a field, validation
    fails loudly instead of silently dropping data.
    """

    model_config = ConfigDict(extra="forbid")


class VariationCategory(str, Enum):
    """The kinds of conceptual variation a student can request.

    Each category tests whether the student can transfer the underlying
    principles to a different situation, rather than just re-solving the
    original problem with new numbers.
    """

    CHANGED_CONDITIONS = "changed_conditions"
    EDGE_CASES = "edge_cases"
    NEGATION_COUNTEREXAMPLE = "negation_counterexample"
    REVERSE_REASONING = "reverse_reasoning"


# Shared constraint so a huge paste can't blow up prompts or cost.
QuestionText = Field(min_length=1, max_length=5000)


class ErrorResponse(StrictModel):
    """Standard error payload returned by every endpoint on failure.

    Gives the extension a single shape to handle for its error and retry
    states, regardless of which endpoint failed.
    """
    code: str = Field(description="Machine-readable error code, e.g. 'ai_invalid_output'")
    message: str = Field(description="Human-readable message safe to show the student")
    retryable: bool = Field(description="Whether the client should offer a retry")