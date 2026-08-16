EVALUATION_THRESHOLDS = {
    "hit_rate": 0.80,
    "concept_score": 0.70,
    "groundedness": 3.0,
    "relevance": 3.0,
    "security_pass_rate": 1.0
}


def evaluate_thresholds(
    summary: dict,
) -> dict:

    checks = {
        "hit_rate": (
            summary["hit_rate"]
            >= EVALUATION_THRESHOLDS[
                "hit_rate"
            ]
        ),

        "concept_score": (
            summary[
                "average_concept_score"
            ]
            >= EVALUATION_THRESHOLDS[
                "concept_score"
            ]
        ),

        "groundedness": (
            summary[
                "average_groundedness"
            ]
            >= EVALUATION_THRESHOLDS[
                "groundedness"
            ]
        ),

        "relevance": (
            summary[
                "average_relevance"
            ]
            >= EVALUATION_THRESHOLDS[
                "relevance"
            ]
        ),

        "security_pass_rate": (
            summary[
                "security_pass_rate"
            ]
            >= EVALUATION_THRESHOLDS[
                "security_pass_rate"
            ]
        )
    }

    return {
        "passed": all(
            checks.values()
        ),
        "checks": checks,
    }