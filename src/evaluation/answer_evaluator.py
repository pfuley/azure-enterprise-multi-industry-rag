def evaluate_answer_concepts(
    answer: str,
    expected_concepts: list[str],
) -> dict:

    if not answer.strip():
        return {
            "matched_concepts": [],
            "missing_concepts": expected_concepts,
            "concept_score": 0.0,
        }

    normalized_answer = answer.lower()

    matched_concepts = [
        concept
        for concept in expected_concepts
        if concept.lower() in normalized_answer
    ]

    missing_concepts = [
        concept
        for concept in expected_concepts
        if concept.lower() not in normalized_answer
    ]

    total = len(expected_concepts)

    concept_score = (
        len(matched_concepts) / total
        if total
        else 1.0
    )

    return {
        "matched_concepts": matched_concepts,
        "missing_concepts": missing_concepts,
        "concept_score": concept_score,
    }