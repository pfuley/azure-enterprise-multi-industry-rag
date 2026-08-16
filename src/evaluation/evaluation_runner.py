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
    answer_question,
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

    Supports:
    - retrieval evaluation
    - concept coverage
    - groundedness
    - answer relevance
    - authorization/refusal testing
    - prompt-injection testing

    Normal evaluation cases reuse the exact retrieved
    chunks for generation and groundedness evaluation.

    Direct prompt-injection cases run through the full
    production answer_question() path so the user
    Prompt Shield is tested correctly.
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

    auth_profile = test_case.get(
        "auth_profile",
        "authorized",
    )

    is_security_case = (
        expect_refusal
        or expect_guardrail_block
    )

    # -----------------------------------------
    # 2. Select authorization profile
    #
    # Normal tests use the AuthorizationContext
    # supplied by run_evaluation.py.
    #
    # Unauthorized tests deliberately create a
    # user who cannot access the IT knowledge
    # base used by the evaluation dataset.
    # -----------------------------------------

    case_auth = auth

    if auth_profile == "unauthorized":

        case_auth = AuthorizationContext(
            user_id=(
                "unauthorized-evaluation-user"
            ),
            roles=[
                "employee",
            ],
            groups=[
                "finance-team",
            ],
            allowed_industries=[
                "financial-services",
            ],
            allowed_departments=[
                "finance",
            ],
            max_classification="internal",
        )

    # -----------------------------------------
    # 3. Retrieval
    #
    # Direct prompt-injection tests should be
    # blocked before retrieval occurs.
    #
    # Therefore we do not manually retrieve
    # anything for those tests.
    # -----------------------------------------

    if expect_guardrail_block:

        search_results = []

    else:

        search_results = (
            semantic_hybrid_search(
                query=question,
                top_k=top_k,
                auth=case_auth,
            )
        )

    # -----------------------------------------
    # 4. Collect retrieved source names
    # -----------------------------------------

    retrieved_sources = [
        result["file_name"]
        for result in search_results
    ]

    # Remove duplicates while preserving order.

    retrieved_sources = list(
        dict.fromkeys(
            retrieved_sources
        )
    )

    # -----------------------------------------
    # 5. Evaluate expected source retrieval
    #
    # Security cases may intentionally have no
    # expected source.
    # -----------------------------------------

    if expected_source:

        source_found = (
            expected_source
            in retrieved_sources
        )

    else:

        source_found = None

    # -----------------------------------------
    # 6. Build exact retrieved context
    #
    # Groundedness must be evaluated against
    # the same evidence used for generation.
    # -----------------------------------------

    if search_results:

        context = build_context(
            search_results
        )

    else:

        context = ""

    # -----------------------------------------
    # 7. Generate answer
    #
    # Prompt-injection cases:
    #     use answer_question()
    #     → full production guardrail path
    #
    # Other cases:
    #     use generate_answer_from_results()
    #     → reuse exact retrieval results
    # -----------------------------------------

    guardrail_blocked = False
    guardrail_reason = None

    try:

        if expect_guardrail_block:

            rag_result = answer_question(
                question=question,
                auth=case_auth,
                top_k=top_k,
            )

        else:

            rag_result = (
                generate_answer_from_results(
                    question=question,
                    search_query=question,
                    search_results=(
                        search_results
                    ),
                )
            )

    except GuardrailBlockedError as error:

        guardrail_blocked = True

        guardrail_reason = str(
            error
        )

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
    # 8. Detect controlled refusal
    #
    # Unauthorized retrieval should return no
    # accessible chunks. The orchestrator then
    # returns its controlled insufficient-
    # information response.
    # -----------------------------------------

    refusal_detected = (
        "could not find sufficient information"
        in answer.lower()
    )

    # -----------------------------------------
    # 9. Evaluate concept coverage
    #
    # Security tests normally have no expected
    # concepts, so they do not affect the
    # concept metric in report.py.
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
    # 10. Evaluate groundedness
    #
    # Directly blocked requests have no answer
    # to evaluate.
    #
    # Expected refusal cases are also security
    # behaviour rather than normal answer-
    # quality cases, so we do not call the LLM
    # groundedness judge for them.
    # -----------------------------------------

    if (
        guardrail_blocked
        or expect_refusal
    ):

        groundedness_result = {
            "grounded": False,
            "score": 0,
            "reason": (
                "Groundedness was not evaluated "
                "because this is a security "
                "refusal or guardrail test."
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
    # 11. Evaluate answer relevance
    #
    # Security refusal/block cases are evaluated
    # through security_passed instead.
    # -----------------------------------------

    if (
        guardrail_blocked
        or expect_refusal
    ):

        relevance_result = {
            "relevant": False,
            "score": 0,
            "reason": (
                "Relevance was not evaluated "
                "because this is a security "
                "refusal or guardrail test."
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
    # 12. Evaluate security expectations
    # -----------------------------------------

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
    # 13. Return complete evaluation result
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

        "auth_profile":
            auth_profile,

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
        # Security evaluation
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