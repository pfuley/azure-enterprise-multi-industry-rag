import json
from pathlib import Path


def load_evaluation_dataset(
    file_path: str,
) -> dict:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Evaluation dataset not found: {file_path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    if "test_cases" not in dataset:
        raise ValueError(
            "Evaluation dataset must contain "
            "'test_cases'."
        )

    return dataset