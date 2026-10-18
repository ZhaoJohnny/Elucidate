"""Schemas for the explain endpoint (Step 5: reveal answer and explanation)."""

from pydantic import Field

from .common import QuestionText, StrictModel
from .variation import Variation


class ExplainRequest(StrictModel):
    """Request body for `POST /api/v1/problems/explain`.

    Includes the original question for context along with the full variation
    being revealed, since the backend doesn't store variations.
    """

    question: str = QuestionText  # the original problem, for context
    variation: Variation


class ExplainResponse(StrictModel):
    """The solution to a variation, shown only after the student asks for it."""

    expected_answer: str = Field(min_length=1)
    explanation: str = Field(
        min_length=1, description="Why the answer is correct, tied back to the principles"
    )