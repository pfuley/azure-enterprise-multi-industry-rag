from src.evaluation.dataset import (
    load_evaluation_dataset,
)
from src.evaluation.evaluation_runner import (
    evaluate_case,
)
from src.evaluation.report import (
    save_evaluation_report,
)
from src.evaluation.thresholds import (
    evaluate_thresholds,
)
from src.security.authorization import (
    AuthorizationContext,
)


DATASET_PATH = (
    "evaluation/eval_dataset.json"
)

REPORT_PATH = (
    "evaluation/reports/latest.json"
)

TOP_K = 3


def main() -> None:

    # -----------------------------------------
    # 1. Load evaluation dataset
    # -----------------------------------------

    dataset = load_evaluation_dataset(
        DATASET_PATH
    )

    # -----------------------------------------
    # 2. Create evaluation authorization
    #    context
    #
    # This represents an authorised IT user
    # who can access the current sample
    # knowledge base.
    # -----------------------------------------

    auth = AuthorizationContext(
        user_id="evaluation-user",
        roles=[
            "employee",
        ],
        groups=[
            "service-desk",
            "it-admins",
        ],
        allowed_industries=[
            "it-support",
        ],
        allowed_departments=[
            "service-desk",
        ],
        max_classification="internal",
    )

    # -----------------------------------------
    # 3. Run evaluation cases
    # -----------------------------------------

    results = []

    print(
        "\nENTERPRISE RAG EVALUATION"
    )

    print(
        "=" * 70
    )

    for test_case in dataset["test_cases"]:

        result = evaluate_case(
            test_case=test_case,
            auth=auth,
            top_k=TOP_K,
        )

        results.append(
            result
        )

        # -------------------------------------
        # Individual test output
        # -------------------------------------

        print(
            f"\nTEST: {result['id']}"
        )

        print(
            "Question:",
            result["question"],
        )

        # -------------------------------------
        # Retrieval details
        # -------------------------------------

        if result.get(
            "expected_source"
        ):
            print(
                "Expected Source:",
                result["expected_source"],
            )

            print(
                "Retrieved Sources:",
                result[
                    "retrieved_sources"
                ],
            )

            print(
                "Source Found:",
                result[
                    "source_found"
                ],
            )

        # -------------------------------------
        # Concept evaluation
        # -------------------------------------

        if result.get(
            "expected_concepts"
        ):
            print(
                "Concept Score:",
                (
                    f"{result['concept_score']:.2%}"
                ),
            )

            print(
                "Matched Concepts:",
                result[
                    "matched_concepts"
                ],
            )

            if result[
                "missing_concepts"
            ]:
                print(
                    "Missing Concepts:",
                    result[
                        "missing_concepts"
                    ],
                )

        # -------------------------------------
        # Security evaluation
        # -------------------------------------

        if result.get(
            "is_security_case"
        ):
            print(
                "Expected Refusal:",
                result[
                    "expect_refusal"
                ],
            )

            print(
                "Refusal Detected:",
                result[
                    "refusal_detected"
                ],
            )

            print(
                "Expected Guardrail Block:",
                result[
                    "expect_guardrail_block"
                ],
            )

            print(
                "Guardrail Blocked:",
                result[
                    "guardrail_blocked"
                ],
            )

            if result.get(
                "guardrail_reason"
            ):
                print(
                    "Guardrail Reason:",
                    result[
                        "guardrail_reason"
                    ],
                )

            print(
                "Security Passed:",
                result[
                    "security_passed"
                ],
            )

        # -------------------------------------
        # Normal answer-quality evaluation
        #
        # Do not treat intentionally blocked
        # guardrail cases as normal answers.
        # -------------------------------------

        if not result.get(
            "expect_guardrail_block",
            False,
        ):
            print(
                "Groundedness:",
                (
                    f"{result['groundedness_score']}/4"
                ),
            )

            print(
                "Grounded:",
                result[
                    "grounded"
                ],
            )

            print(
                "Relevance:",
                (
                    f"{result['relevance_score']}/4"
                ),
            )

            print(
                "Relevant:",
                result[
                    "relevant"
                ],
            )

            print(
                "Groundedness Reason:",
                result[
                    "groundedness_reason"
                ],
            )

            print(
                "Relevance Reason:",
                result[
                    "relevance_reason"
                ],
            )

    # -----------------------------------------
    # 4. Save JSON evaluation report
    # -----------------------------------------

    report = save_evaluation_report(
        results=results,
        output_path=REPORT_PATH,
        top_k=TOP_K,
    )

    summary = report[
        "summary"
    ]

    # -----------------------------------------
    # 5. Print overall metrics
    # -----------------------------------------

    print("\n")
    print(
        "=" * 70
    )

    print(
        "OVERALL RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        "Total Test Cases:",
        summary[
            "test_cases"
        ],
    )

    print(
        "Retrieval Cases:",
        summary[
            "retrieval_cases"
        ],
    )

    print(
        "Security Cases:",
        summary[
            "security_cases"
        ],
    )

    print(
        f"Hit Rate@{TOP_K}:",
        (
            f"{summary['hit_rate']:.2%}"
        ),
    )

    print(
        "Average Concept Score:",
        (
            f"{summary['average_concept_score']:.2%}"
        ),
    )

    print(
        "Average Groundedness:",
        (
            f"{summary['average_groundedness']:.2f}/4"
        ),
    )

    print(
        "Average Relevance:",
        (
            f"{summary['average_relevance']:.2f}/4"
        ),
    )

    print(
        "Security Pass Rate:",
        (
            f"{summary['security_pass_rate']:.2%}"
        ),
    )

    # -----------------------------------------
    # 6. Apply evaluation quality thresholds
    # -----------------------------------------

    threshold_result = (
        evaluate_thresholds(
            summary
        )
    )

    print("\n")
    print(
        "=" * 70
    )

    print(
        "QUALITY GATE"
    )

    print(
        "=" * 70
    )

    for metric, passed in (
        threshold_result[
            "checks"
        ].items()
    ):
        print(
            f"{metric}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    # -----------------------------------------
    # 7. Print overall quality-gate result
    # -----------------------------------------

    overall_status = (
        "PASS"
        if threshold_result[
            "passed"
        ]
        else "FAIL"
    )

    print(
        "\nOverall:",
        overall_status,
    )

    print(
        "\nEvaluation report saved to:",
        REPORT_PATH,
    )

    # -----------------------------------------
    # 8. Return a failing process exit code
    #    when quality thresholds are not met.
    #
    # Later GitHub Actions will use this to
    # stop CI/CD when RAG quality regresses.
    # -----------------------------------------

    if not threshold_result[
        "passed"
    ]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()