from src.evaluation.dataset import (
    load_evaluation_dataset,
)
from src.evaluation.evaluation_runner import (
    evaluate_case,
)
from src.security.authorization import (
    AuthorizationContext,
)


dataset = load_evaluation_dataset(
    "evaluation/eval_dataset.json"
)


auth = AuthorizationContext(
    user_id="evaluation-user",
    roles=["employee"],
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


print("\nGROUNDING EVALUATION")
print("=" * 60)


for test_case in dataset["test_cases"]:

    result = evaluate_case(
        test_case=test_case,
        auth=auth,
        top_k=3,
    )

    print(
        f"\nTEST: {result['id']}"
    )

    print(
        "Question:",
        result["question"],
    )

    print(
        "Source Found:",
        result["source_found"],
    )

    print(
        "Concept Score:",
        f"{result['concept_score']:.2%}",
    )

    print(
        "Grounded:",
        result["grounded"],
    )

    print(
        "Groundedness Score:",
        f"{result['groundedness_score']}/4",
    )

    print(
        "Reason:",
        result["groundedness_reason"],
    )