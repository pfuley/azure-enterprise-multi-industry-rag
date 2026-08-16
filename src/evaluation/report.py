import json
from datetime import datetime, timezone
from pathlib import Path


def save_evaluation_report(
    results: list[dict],
    output_path: str,
    top_k: int = 3,
) -> dict:
    """
    Build and save a JSON evaluation report.

    The report contains:
    - overall retrieval metrics
    - concept coverage
    - groundedness
    - relevance
    - security pass rate
    - detailed per-test results
    """

    # -----------------------------------------
    # 1. Basic totals
    # -----------------------------------------

    total_cases = len(results)

    # -----------------------------------------
    # 2. Retrieval hit rate
    #
    # Only normal cases with an expected source
    # should contribute to retrieval hit rate.
    # -----------------------------------------

    retrieval_cases = [
        result
        for result in results
        if result.get("expected_source")
    ]

    source_hits = sum(
        1
        for result in retrieval_cases
        if result.get("source_found")
    )

    hit_rate = (
        source_hits / len(retrieval_cases)
        if retrieval_cases
        else 1.0
    )

    # -----------------------------------------
    # 3. Concept coverage
    #
    # Only cases with expected concepts should
    # contribute to this metric.
    # -----------------------------------------

    concept_cases = [
        result
        for result in results
        if result.get("expected_concepts")
    ]

    average_concept_score = (
        sum(
            result.get(
                "concept_score",
                0.0,
            )
            for result in concept_cases
        )
        / len(concept_cases)
        if concept_cases
        else 1.0
    )

    # -----------------------------------------
    # 4. Groundedness
    #
    # Security cases that intentionally block
    # the request should not reduce normal
    # groundedness metrics.
    # -----------------------------------------

    groundedness_cases = [
        result
        for result in results
        if not result.get(
            "expect_guardrail_block",
            False,
        )
    ]

    average_groundedness = (
        sum(
            result.get(
                "groundedness_score",
                0,
            )
            for result in groundedness_cases
        )
        / len(groundedness_cases)
        if groundedness_cases
        else 0.0
    )

    # -----------------------------------------
    # 5. Answer relevance
    # -----------------------------------------

    relevance_cases = [
        result
        for result in results
        if not result.get(
            "expect_guardrail_block",
            False,
        )
    ]

    average_relevance = (
        sum(
            result.get(
                "relevance_score",
                0,
            )
            for result in relevance_cases
        )
        / len(relevance_cases)
        if relevance_cases
        else 0.0
    )

    # -----------------------------------------
    # 6. Security evaluation
    # -----------------------------------------

    security_cases = [
        result
        for result in results
        if result.get(
            "is_security_case",
            False,
        )
    ]

    security_pass_count = sum(
        1
        for result in security_cases
        if result.get(
            "security_passed",
            False,
        )
    )

    security_pass_rate = (
        security_pass_count
        / len(security_cases)
        if security_cases
        else 1.0
    )

    # -----------------------------------------
    # 7. Build summary
    # -----------------------------------------

    summary = {
        "test_cases":
            total_cases,

        "retrieval_cases":
            len(retrieval_cases),

        "security_cases":
            len(security_cases),

        "hit_rate":
            hit_rate,

        "average_concept_score":
            average_concept_score,

        "average_groundedness":
            average_groundedness,

        "average_relevance":
            average_relevance,

        "security_pass_rate":
            security_pass_rate,
    }

    # -----------------------------------------
    # 8. Build final report
    # -----------------------------------------

    report = {
        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "top_k":
            top_k,

        "summary":
            summary,

        "results":
            results,
    }

    # -----------------------------------------
    # 9. Ensure report directory exists
    # -----------------------------------------

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------
    # 10. Save JSON report
    # -----------------------------------------

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    # -----------------------------------------
    # 11. Return report for quality gates
    # -----------------------------------------

    return report