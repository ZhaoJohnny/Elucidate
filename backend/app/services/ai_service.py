"""Real AI implementations of analyze, variations, and explain."""

from collections import Counter

from app.prompts import analyze as analyze_prompt
from app.prompts import explain as explain_prompt
from app.prompts import variations as variations_prompt
from app.schemas import (
    AnalysisResponse,
    ExplainResponse,
    Variation,
    VariationCategory,
)
from app.schemas.variation import VariationDrafts

from .ai_client import generate_structured


def analyze(question: str) -> AnalysisResponse:
    return generate_structured(
        system=analyze_prompt.SYSTEM,
        user=analyze_prompt.build_user(question),
        schema=AnalysisResponse,
    )


def variations(
    question: str,
    analysis: AnalysisResponse,
    categories: list[VariationCategory],
    count: int,
) -> list[Variation]:
    def check(result: VariationDrafts) -> None:
        got = Counter(v.category for v in result.variations)
        for c in categories:
            if got[c] != count:
                raise ValueError(
                    f"Expected exactly {count} variation(s) for '{c.value}', got {got[c]}."
                )
        extra = set(got) - set(categories)
        if extra:
            raise ValueError(f"Unrequested categories returned: {sorted(e.value for e in extra)}.")

    drafts = generate_structured(
        system=variations_prompt.SYSTEM,
        user=variations_prompt.build_user(question, analysis, categories, count),
        schema=VariationDrafts,
        validate=check,
    )
    # Variation() assigns a fresh id via its default_factory.
    return [Variation(**d.model_dump()) for d in drafts.variations]


def explain(question: str, variation: Variation) -> ExplainResponse:
    return generate_structured(
        system=explain_prompt.SYSTEM,
        user=explain_prompt.build_user(question, variation),
        schema=ExplainResponse,
    )