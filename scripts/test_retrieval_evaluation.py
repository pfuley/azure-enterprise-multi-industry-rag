from src.evaluation.dataset import (
    load_evaluation_dataset,
)
from src.evaluation.retrieval_evaluator import (
    evaluate_retrieval_case,
)
from src.security.authorization import (
    AuthorizationContext,
)


DATASET_PATH = (
    "evaluation/eval_dataset.json"
)


dataset = load_evaluation_dataset(
    DATASET_PATH
)


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


print("\nRETRIEVAL EVALUATION")
print("=" * 60)


passed = 0


for test_case in dataset["test_cases"]:

    result = evaluate_retrieval_case(
        test_case=test_case,
        auth=auth,
        top_k=3,
    )

    print(
        f"\nTest: {result['id']}"
    )

    print(
        "Question:",
        result["question"],
    )

    print(
        "Expected Source:",
        result["expected_source"],
    )

    print(
        "Retrieved Sources:",
        result["retrieved_sources"],
    )

    print(
        "PASS:"
        if result["source_found"]
        else "FAIL:"
    )

    print(
        result["source_found"]
    )

    if result["source_found"]:
        passed += 1


total = len(
    dataset["test_cases"]
)


score = (
    passed / total
    if total
    else 0
)


print("\nSUMMARY")
print("=" * 60)

print(
    f"Passed: {passed}/{total}"
)

print(
    f"Hit Rate@3: {score:.2%}"
)