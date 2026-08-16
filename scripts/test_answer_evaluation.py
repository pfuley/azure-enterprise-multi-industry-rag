from src.evaluation.answer_evaluator import (
    evaluate_answer_concepts,
)
from src.evaluation.dataset import (
    load_evaluation_dataset,
)
from src.rag.chat_service import RAGChatService
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


print("\nANSWER EVALUATION")
print("=" * 60)


total_score = 0.0


for test_case in dataset["test_cases"]:

    # Create a fresh conversation for every
    # evaluation case.
    chat = RAGChatService(
        auth=auth
    )

    result = chat.ask(
        test_case["question"]
    )

    evaluation = evaluate_answer_concepts(
        answer=result["answer"],
        expected_concepts=(
            test_case["expected_concepts"]
        ),
    )

    print(
        f"\nTEST: {test_case['id']}"
    )

    print(
        "Question:",
        test_case["question"],
    )

    print(
        "\nAnswer:"
    )

    print(
        result["answer"]
    )

    print(
        "\nExpected Concepts:",
        test_case["expected_concepts"],
    )

    print(
        "Matched Concepts:",
        evaluation[
            "matched_concepts"
        ],
    )

    print(
        "Missing Concepts:",
        evaluation[
            "missing_concepts"
        ],
    )

    print(
        "Concept Score:",
        f"{evaluation['concept_score']:.2%}",
    )

    total_score += (
        evaluation["concept_score"]
    )


total_cases = len(
    dataset["test_cases"]
)


average_score = (
    total_score / total_cases
    if total_cases
    else 0
)


print("\nOVERALL")
print("=" * 60)

print(
    "Test Cases:",
    total_cases,
)

print(
    "Average Concept Score:",
    f"{average_score:.2%}",
)