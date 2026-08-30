from dataclasses import dataclass


WEIGHTS = {
    "investment": 0.25,
    "jobs": 0.20,
    "export": 0.15,
    "environmental": 0.15,
    "financial": 0.10,
    "technology": 0.10,
    "readiness": 0.05,
}


@dataclass(frozen=True)
class ScoreResult:
    total: float
    category: str
    components: dict[str, float]


def normalize(value: float, excellent: float) -> float:
    """Convert a non-negative value to a score from 0 to 100."""
    if value < 0:
        raise ValueError("Scoring values cannot be negative")
    return min(value / excellent * 100, 100.0)


def category_for(score: float) -> str:
    if score >= 80:
        return "Strategic Priority"
    if score >= 60:
        return "Strong Opportunity"
    if score >= 40:
        return "Requires Development"
    return "Low Priority"


def calculate_score(
    investment_usd_m: float,
    jobs: int,
    export_percent: float,
    environmental_score: float,
    financial_score: float,
    technology_score: float,
    readiness_score: float,
) -> ScoreResult:
    """Calculate a transparent weighted score for an investment lead."""
    components = {
        "investment": normalize(investment_usd_m, 100),
        "jobs": normalize(jobs, 1000),
        "export": normalize(export_percent, 100),
        "environmental": normalize(environmental_score, 10),
        "financial": normalize(financial_score, 10),
        "technology": normalize(technology_score, 10),
        "readiness": normalize(readiness_score, 10),
    }
    total = round(sum(components[key] * WEIGHTS[key] for key in WEIGHTS), 1)
    return ScoreResult(total, category_for(total), components)
