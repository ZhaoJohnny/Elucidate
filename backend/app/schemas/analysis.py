from pydantic import Field

from .common import QuestionText, StrictModel


class AnalyzeRequest(StrictModel):
    question: str = QuestionText


class AnalysisResponse(StrictModel):
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