"""Hardcoded responses for the three sample questions.

Used to lock the API contract before any AI is involved. Questions are matched
by a plain-text keyword (not LaTeX), so matching is robust to how math renders.
Unrecognized questions get a generic placeholder response.
"""

from app.schemas import (
    AnalysisResponse,
    ExplainResponse,
    Variation,
    VariationCategory as Cat,
)

# Explanations are looked up by variation id, since the backend is stateless.
EXPLANATIONS: dict[str, ExplainResponse] = {}


def _variation(
    sample_id: str,
    category: Cat,
    question: str,
    modified_conditions: list[str],
    learning_objective: str,
    answer: str,
    explanation: str,
) -> Variation:
    """Build a Variation with a deterministic id and register its explanation."""
    v = Variation(
        id=f"{sample_id}:{category.value}",
        category=category,
        question=question,
        modified_conditions=modified_conditions,
        learning_objective=learning_objective,
    )
    EXPLANATIONS[v.id] = ExplainResponse(expected_answer=answer, explanation=explanation)
    return v


SAMPLES: dict[str, dict] = {
    # ---------------------------------------------------------------- calculus
    "calc-001": {
        "keyword": "absolute maximum",
        "analysis": AnalysisResponse(
            summary="Find the largest value of a cubic function over a closed interval.",
            principles=[
                "Extreme Value Theorem: a continuous function on a closed, bounded interval attains an absolute maximum and minimum.",
                "Closed interval method: compare f at critical points and at the endpoints.",
                "Critical points occur where f'(x) = 0 or f' is undefined.",
            ],
            assumptions=[
                "f is continuous (and differentiable) on [-2, 2].",
                "The interval is closed and bounded, so the maximum is guaranteed to exist.",
            ],
            constraints=[
                "Endpoints must be checked, since the maximum can occur there.",
                "Only critical points inside the interval are candidates.",
            ],
            reasoning="Setting f'(x) = 3x^2 - 3 = 0 gives x = ±1. Comparing f(-2) = -2, f(-1) = 2, f(1) = -2, f(2) = 2, the absolute maximum is 2, attained at both x = -1 (interior) and x = 2 (endpoint).",
        ),
        "variations": [
            _variation(
                "calc-001", Cat.CHANGED_CONDITIONS,
                "Find the absolute maximum of f(x) = x^3 - 3x on the interval [-2, 1].",
                ["Upper endpoint changed from 2 to 1"],
                "Recognize that moving an endpoint changes which candidates are valid.",
                "2, attained at x = -1",
                "x = 2 is no longer in the interval. Candidates are f(-2) = -2, f(-1) = 2, and f(1) = -2, so the maximum is 2 at the interior critical point x = -1.",
            ),
            _variation(
                "calc-001", Cat.EDGE_CASES,
                "Find the absolute maximum of f(x) = x^3 - 3x on the open interval (-2, 2). Does the Extreme Value Theorem guarantee that one exists?",
                ["Closed interval replaced by an open interval"],
                "Understand what the Extreme Value Theorem does and does not guarantee.",
                "The maximum is 2, attained at x = -1. The theorem does not guarantee it.",
                "The theorem requires a closed interval, so it gives no guarantee here. A maximum still exists because f(-1) = 2 and f(x) - 2 = (x + 1)^2 (x - 2) ≤ 0 for all x < 2. The endpoint value 2 is simply not attained.",
            ),
            _variation(
                "calc-001", Cat.NEGATION_COUNTEREXAMPLE,
                "A student claims that the absolute maximum of a differentiable function on a closed interval always occurs where f'(x) = 0. For f(x) = x^3 - 3x, find an interval that is a counterexample.",
                ["Key assumption (maximum occurs at a critical point) is false"],
                "Recognize that endpoints can be absolute extrema without f' = 0.",
                "For example [0, 2]: the maximum is f(2) = 2, but f'(2) = 9 ≠ 0.",
                "On [0, 2] the only critical point is x = 1 with f(1) = -2. Endpoint values are f(0) = 0 and f(2) = 2, so the maximum occurs at the endpoint x = 2, where the derivative is not zero.",
            ),
            _variation(
                "calc-001", Cat.REVERSE_REASONING,
                "The function f(x) = x^3 - 3x has absolute maximum value 2 on the interval [-2, b]. What are the possible values of b?",
                ["Right endpoint is unknown; the answer is given"],
                "Work backward from a result to the conditions that produce it.",
                "-1 ≤ b ≤ 2",
                "f rises to 2 at x = -1, falls to -2 at x = 1, then rises to 2 again at x = 2. For b < -1 the maximum is f(b) < 2. For -1 ≤ b ≤ 2 the maximum is exactly 2. For b > 2, f(b) > 2.",
            ),
        ],
    },
    # ----------------------------------------------------------------- physics
    "phys-001": {
        "keyword": "thrown straight up",
        "analysis": AnalysisResponse(
            summary="Find the maximum height of an object launched vertically upward.",
            principles=[
                "Constant-acceleration kinematics: v^2 = v0^2 - 2g·h.",
                "At maximum height the instantaneous vertical velocity is zero.",
                "Equivalent view: initial kinetic energy converts fully to gravitational potential energy.",
            ],
            assumptions=[
                "Air resistance is negligible.",
                "g is constant over the whole flight.",
                "Height is measured from the release point.",
            ],
            constraints=[
                "Motion is purely vertical.",
                "Sign convention must be consistent (upward positive means acceleration is -g).",
            ],
            reasoning="Setting v = 0 gives h = v0^2 / (2g) = 400 / 19.6 ≈ 20.4 m.",
        ),
        "variations": [
            _variation(
                "phys-001", Cat.CHANGED_CONDITIONS,
                "The same ball is thrown straight up at 20 m/s on the Moon, where g = 1.6 m/s^2. What maximum height does it reach?",
                ["Gravitational acceleration changed from 9.8 to 1.6 m/s^2"],
                "See how the result depends on g through h = v0^2 / (2g).",
                "125 m",
                "h = v0^2 / (2g) = 400 / 3.2 = 125 m. Lower gravity means the ball decelerates more slowly and rises much higher.",
            ),
            _variation(
                "phys-001", Cat.EDGE_CASES,
                "A ball is launched at 20 m/s at an angle θ above the horizontal (g = 9.8 m/s^2, no air resistance). Find its maximum height at θ = 0° and θ = 90°, and describe what happens in between.",
                ["Launch direction generalized from straight up to angle θ"],
                "Check the formula at its boundary cases using only the vertical velocity component.",
                "0 m at θ = 0°; about 20.4 m at θ = 90°; height increases with θ.",
                "Only the vertical component v0 sin θ matters: h = (v0 sin θ)^2 / (2g). At θ = 0° this is 0, and at θ = 90° it equals the original answer, about 20.4 m. Height increases smoothly with θ in between.",
            ),
            _variation(
                "phys-001", Cat.NEGATION_COUNTEREXAMPLE,
                "A student says a heavier ball will rise higher than a lighter one thrown at the same speed, because it has more energy. With no air resistance, explain why this is false.",
                ["Assumption that mass affects maximum height is challenged"],
                "Recognize that mass cancels in the energy and kinematic analyses.",
                "False: maximum height is independent of mass.",
                "Kinetic energy (1/2)mv0^2 converts to potential energy mgh, and the mass cancels, leaving h = v0^2 / (2g). The kinematic equation never involved mass at all.",
            ),
            _variation(
                "phys-001", Cat.REVERSE_REASONING,
                "A ball thrown straight up reaches a maximum height of 45 m (g = 9.8 m/s^2, no air resistance). What was its initial speed?",
                ["Maximum height given; initial speed is unknown"],
                "Invert the relationship h = v0^2 / (2g).",
                "About 29.7 m/s",
                "v0 = sqrt(2gh) = sqrt(2 × 9.8 × 45) = sqrt(882) ≈ 29.7 m/s.",
            ),
        ],
    },
    # -------------------------------------------------------- linear algebra
    "la-001": {
        "keyword": "invertible",
        "analysis": AnalysisResponse(
            summary="Decide whether a 2×2 matrix has an inverse and justify the decision.",
            principles=[
                "A square matrix is invertible if and only if its determinant is nonzero.",
                "Equivalently, invertibility means linearly independent columns (full rank).",
            ],
            assumptions=[
                "A is a square matrix with real entries.",
            ],
            constraints=[
                "Only square matrices can be invertible.",
            ],
            reasoning="det(A) = 1·4 - 2·2 = 0, and the second row is twice the first, so the rows are linearly dependent. A is not invertible.",
        ),
        "variations": [
            _variation(
                "la-001", Cat.CHANGED_CONDITIONS,
                "Change the bottom-right entry of A from 4 to 5, giving B = [[1, 2], [2, 5]]. Is B invertible?",
                ["Entry a22 changed from 4 to 5"],
                "See how a small change can break linear dependence.",
                "Yes, B is invertible.",
                "det(B) = 1·5 - 2·2 = 1 ≠ 0, so B is invertible. The rows (1, 2) and (2, 5) are no longer multiples of each other.",
            ),
            _variation(
                "la-001", Cat.EDGE_CASES,
                "Is the 3×2 matrix C = [[1, 2], [3, 4], [5, 6]] invertible? Justify your answer.",
                ["Matrix is no longer square"],
                "Recall that invertibility is only defined for square matrices.",
                "No: C is not square, so it has no inverse.",
                "The determinant and the inverse are only defined for square matrices. C maps R^2 to R^3, so it cannot be a bijection.",
            ),
            _variation(
                "la-001", Cat.NEGATION_COUNTEREXAMPLE,
                "A student claims that any 2×2 matrix with no zero entries is invertible. Give a counterexample.",
                ["Claim that nonzero entries guarantee invertibility is challenged"],
                "Understand that invertibility depends on linear independence, not on entries being nonzero.",
                "For example [[1, 1], [1, 1]].",
                "All entries are nonzero, but det = 1·1 - 1·1 = 0 and the rows are identical, so the matrix is not invertible.",
            ),
            _variation(
                "la-001", Cat.REVERSE_REASONING,
                "The matrix D = [[2, a], [4, 6]] is not invertible. What is a?",
                ["Singularity given; an entry is unknown"],
                "Work backward from det = 0 to a missing entry.",
                "a = 3",
                "Not invertible means det(D) = 2·6 - 4a = 12 - 4a = 0, so a = 3. Check: the rows (2, 3) and (4, 6) are proportional.",
            ),
        ],
    },
}


# --------------------------------------------------------------------- lookup
_GENERIC_ANALYSIS = AnalysisResponse(
    summary="[Mock] Generic analysis for an unrecognized question.",
    principles=["[Mock] Placeholder principle."],
    assumptions=["[Mock] Placeholder assumption."],
    constraints=["[Mock] Placeholder constraint."],
    reasoning="[Mock] This question is not one of the three sample questions.",
)

_GENERIC_EXPLANATION = ExplainResponse(
    expected_answer="[Mock] Placeholder answer.",
    explanation="[Mock] No stored explanation for this variation.",
)


def find_sample_id(question: str) -> str | None:
    """Return the id of the sample question matching the text, if any."""
    text = question.lower()
    for sample_id, sample in SAMPLES.items():
        if sample["keyword"] in text:
            return sample_id
    return None


def get_analysis(question: str) -> AnalysisResponse:
    sample_id = find_sample_id(question)
    return SAMPLES[sample_id]["analysis"] if sample_id else _GENERIC_ANALYSIS


def get_variations(question: str, categories: list[Cat]) -> list[Variation]:
    """Return one mock variation per requested category."""
    sample_id = find_sample_id(question)
    if sample_id is None:
        return [
            Variation(
                id=f"generic:{c.value}",
                category=c,
                question=f"[Mock] Placeholder {c.value} question.",
                modified_conditions=["[Mock] Placeholder change."],
                learning_objective="[Mock] Placeholder objective.",
            )
            for c in categories
        ]
    by_category = {v.category: v for v in SAMPLES[sample_id]["variations"]}
    return [by_category[c] for c in categories]


def get_explanation(variation: Variation) -> ExplainResponse:
    return EXPLANATIONS.get(variation.id, _GENERIC_EXPLANATION)