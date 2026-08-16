from src.evaluation.dataset import (
    load_evaluation_dataset,
)


DATASET_PATH = (
    "evaluation/eval_dataset.json"
)


dataset = load_evaluation_dataset(
    DATASET_PATH
)


print("\nEVALUATION DATASET")
print("=" * 60)

print(
    "Name:",
    dataset["dataset_name"],
)

print(
    "Version:",
    dataset["version"],
)

print(
    "Test Cases:",
    len(dataset["test_cases"]),
)


print("\nTEST CASES")
print("=" * 60)


for test_case in dataset["test_cases"]:

    print(
        f"\nID: {test_case['id']}"
    )

    print(
        f"Question: "
        f"{test_case['question']}"
    )

    print(
        f"Expected Source: "
        f"{test_case['expected_source']}"
    )