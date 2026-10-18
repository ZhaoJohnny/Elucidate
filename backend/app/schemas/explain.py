from pydantic import Field

from .common import QuestionText, StrictModel
from .variation import Variation


class ExplainRequest(StrictModel):
    question: str = QuestionText  # the original problem, for context
    variation: Variation


class ExplainResponse(StrictModel):
    expected_answer: str = Field(min_length=1)
    explanation: str = Field(
        min_length=1, description="Why the answer is correct, tied back to the principles"
    )