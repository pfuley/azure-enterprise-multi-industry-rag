from src.evaluation.answer_evaluator import (
    evaluate_answer_concepts,
)
from src.evaluation.groundedness_evaluator import (
    evaluate_groundedness,
)
from src.evaluation.relevance_evaluator import (
    evaluate_answer_relevance,
)
from src.guardrails.exceptions import (
    GuardrailBlockedError,
)
from src.rag.context_builder import (
    build_context,
)
from src.rag.orchestrator import (
    generate_answer_from_results,
)
from src.retrieval.vector_search import (
    semantic_hybrid_search,
)
from src.security.authorization import (
    AuthorizationContext,
)


def evaluate_case(
    test_case: dict,
    auth: AuthorizationContext,
    top_k: int = 3,
) -> dict:
    """
    Evaluate one RAG test case.

    The same retrieved chunks are used for:
    - source evaluation
    - answer generation
    - groundedness evaluation

    Security and guardrail cases are also evaluated.
    """

    # -----------------------------------------
    # 1. Read evaluation case
    # -----------------------------------------

    question = test_case["question"]

    expected_source = test_case.get(
        "expected_source"
    )

    expected_concepts = test_case.get(
        "expected_concepts",
        [],
    )

    expect_refusal = test_case.get(
        "expect_refusal",
        False,
    )

    expect_guardrail_block = test_case.get(
        "expect_guardrail_block",
        False,
    )

    # -----------------------------------------
    # 2. Run retrieval once
    # -----------------------------------------

    search_results = semantic_hybrid_search(
        query=question,
        top_k=top_k,
        auth=auth,
    )

    # -----------------------------------------
    # 3. Collect unique retrieved sources
    # -----------------------------------------

    retrieved_sources = [
        result["file_name"]
        for result in search_results
    ]

    retrieved_sources = list(
        dict.fromkeys(
            retrieved_sources
        )
    )

    # -----------------------------------------
    # 4. Evaluate expected source retrieval
    #
    # Negative/security cases may not require
    # an expected source.
    # -----------------------------------------

    if expected_source:
        source_found = (
            expected_source
            in retrieved_sources
        )
    else:
        source_found = None

    # -----------------------------------------
    # 5. Build exact retrieved context
    # -----------------------------------------

    context = build_context(
        search_results
    )

    # -----------------------------------------
    # 6. Generate answer using the exact
    #    retrieved results
    # -----------------------------------------

    guardrail_blocked = False
    guardrail_reason = None

    try:
        rag_result = (
            generate_answer_from_results(
                question=question,
                search_query=question,
                search_results=search_results,
            )
        )

    except GuardrailBlockedError as error:
        guardrail_blocked = True
        guardrail_reason = str(error)

        rag_result = {
            "answer": "",
            "sources": [],
            "search_query": question,
            "retrieval_trace": [],
        }

    answer = rag_result[
        "answer"
    ]

    # -----------------------------------------
    # 7. Detect expected refusal
    # -----------------------------------------

    refusal_detected = (
        "could not find sufficient information"
        in answer.lower()
    )

    # -----------------------------------------
    # 8. Evaluate concept coverage
    #
    # Security tests may have no expected
    # concepts.
    # -----------------------------------------

    concept_result = (
        evaluate_answer_concepts(
            answer=answer,
            expected_concepts=(
                expected_concepts
            ),
        )
    )

    # -----------------------------------------
    # 9. Evaluate groundedness
    #
    # Skip normal groundedness scoring when
    # a guardrail intentionally blocked the
    # request.
    # -----------------------------------------

    if guardrail_blocked:
        groundedness_result = {
            "grounded": False,
            "score": 0,
            "reason": (
                "Groundedness was not evaluated "
                "because the request was blocked "
                "by a guardrail."
            ),
        }

    else:
        groundedness_result = (
            evaluate_groundedness(
                question=question,
                answer=answer,
                context=context,
            )
        )

    # -----------------------------------------
    # 10. Evaluate answer relevance
    #
    # Skip relevance when guardrail blocking
    # is the expected behaviour.
    # -----------------------------------------

    if guardrail_blocked:
        relevance_result = {
            "relevant": False,
            "score": 0,
            "reason": (
                "Relevance was not evaluated "
                "because the request was blocked "
                "by a guardrail."
            ),
        }

    else:
        relevance_result = (
            evaluate_answer_relevance(
                question=question,
                answer=answer,
            )
        )

    # -----------------------------------------
    # 11. Evaluate security expectations
    # -----------------------------------------

    is_security_case = (
        expect_refusal
        or expect_guardrail_block
    )

    security_passed = True

    if expect_refusal:
        security_passed = (
            security_passed
            and refusal_detected
        )

    if expect_guardrail_block:
        security_passed = (
            security_passed
            and guardrail_blocked
        )

    # -----------------------------------------
    # 12. Return complete evaluation result
    # -----------------------------------------

    return {
        # -------------------------------------
        # Test metadata
        # -------------------------------------

        "id":
            test_case["id"],

        "question":
            question,

        "answer":
            answer,

        "top_k":
            top_k,

        # -------------------------------------
        # Retrieval evaluation
        # -------------------------------------

        "expected_source":
            expected_source,

        "retrieved_sources":
            retrieved_sources,

        "source_found":
            source_found,

        # -------------------------------------
        # Concept evaluation
        # -------------------------------------

        "expected_concepts":
            expected_concepts,

        "matched_concepts":
            concept_result[
                "matched_concepts"
            ],

        "missing_concepts":
            concept_result[
                "missing_concepts"
            ],

        "concept_score":
            concept_result[
                "concept_score"
            ],

        # -------------------------------------
        # Groundedness evaluation
        # -------------------------------------

        "grounded":
            groundedness_result[
                "grounded"
            ],

        "groundedness_score":
            groundedness_result[
                "score"
            ],

        "groundedness_reason":
            groundedness_result[
                "reason"
            ],

        # -------------------------------------
        # Relevance evaluation
        # -------------------------------------

        "relevant":
            relevance_result[
                "relevant"
            ],

        "relevance_score":
            relevance_result[
                "score"
            ],

        "relevance_reason":
            relevance_result[
                "reason"
            ],

        # -------------------------------------
        # Security / refusal evaluation
        # -------------------------------------

        "is_security_case":
            is_security_case,

        "expect_refusal":
            expect_refusal,

        "refusal_detected":
            refusal_detected,

        "expect_guardrail_block":
            expect_guardrail_block,

        "guardrail_blocked":
            guardrail_blocked,

        "guardrail_reason":
            guardrail_reason,

        "security_passed":
            security_passed,

        # -------------------------------------
        # RAG diagnostics
        # -------------------------------------

        "search_query":
            rag_result.get(
                "search_query",
                question,
            ),

        "sources":
            rag_result.get(
                "sources",
                [],
            ),

        "retrieval_trace":
            rag_result.get(
                "retrieval_trace",
                [],
            ),
    }