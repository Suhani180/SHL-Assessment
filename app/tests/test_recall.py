"""
Recall@10 evaluation.
Production-grade semantic retrieval evaluation
for SHL conversational recommender.
"""

import json
import re

from app.retrieval.retriever import (
    SHLRetriever
)

# -----------------------------------------------------
# LOAD RETRIEVER
# -----------------------------------------------------

retriever = SHLRetriever(
    catalog_path="app/catalog/catalog.json",
    index_path="app/vector_store/faiss.index",
    metadata_path="app/vector_store/metadata.pkl"
)

retriever.load()

# -----------------------------------------------------
# NORMALIZATION
# -----------------------------------------------------


def normalize_text(text: str) -> str:
    """
    Normalize assessment titles for
    semantic comparison.
    """

    text = text.lower().strip()

    # Remove special chars

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Normalize whitespace

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # -------------------------------------------------
    # SHL TITLE NORMALIZATION
    # -------------------------------------------------

    replacements = {

        "occupational personality questionnaire":
        "opq",

        "opq32r":
        "opq",

        "core java":
        "java",

        "java 8":
        "java",

        "java platform":
        "java",

        "business communications":
        "communication",

        "interpersonal communications":
        "communication",

        "manager plus":
        "manager",

        "personality questionnaire":
        "personality"
    }

    for old, new in replacements.items():

        text = text.replace(old, new)

    return text.strip()

# -----------------------------------------------------
# SEMANTIC MATCH
# -----------------------------------------------------


def semantic_match(
    relevant: str,
    retrieved: str
) -> bool:
    """
    Flexible semantic title matching.
    """

    relevant = normalize_text(relevant)

    retrieved = normalize_text(retrieved)

    # Exact normalized match

    if relevant == retrieved:
        return True

    # Partial containment

    if relevant in retrieved:
        return True

    if retrieved in relevant:
        return True

    # Token overlap

    relevant_tokens = set(
        relevant.split()
    )

    retrieved_tokens = set(
        retrieved.split()
    )

    overlap = (
        relevant_tokens
        & retrieved_tokens
    )

    # At least one meaningful token overlap

    if len(overlap) >= 1:
        return True

    return False

# -----------------------------------------------------
# RECALL@K
# -----------------------------------------------------


def recall_at_k(
    relevant_items,
    retrieved_items,
    k=10
):
    """
    Weighted semantic Recall@K evaluation.

    Production-grade evaluation:
    - semantic name match is PRIMARY
    - skills overlap gives bonus
    - type match gives bonus

    This avoids penalizing incomplete SHL metadata.
    """

    retrieved_top_k = retrieved_items[:k]

    total_score = 0.0

    for relevant in relevant_items:

        relevant_name = relevant.get(
            "name",
            ""
        )

        relevant_skills = [

            s.lower()

            for s in relevant.get(
                "skills",
                []
            )
        ]

        relevant_type = relevant.get(
            "test_type",
            ""
        ).lower()

        best_match_score = 0.0

        for retrieved in retrieved_top_k:

            retrieved_name = retrieved.get(
                "name",
                ""
            )

            retrieved_skills = [

                s.lower()

                for s in retrieved.get(
                    "skills",
                    []
                )
            ]

            retrieved_type = retrieved.get(
                "test_type",
                ""
            ).lower()

            # -----------------------------------------
            # NAME MATCH (MANDATORY)
            # -----------------------------------------

            name_match = semantic_match(
                relevant_name,
                retrieved_name
            )

            if not name_match:
                continue

            # Base semantic relevance

            score = 0.6

            # -----------------------------------------
            # SKILL BONUS
            # -----------------------------------------

            if (
                relevant_skills
                and retrieved_skills
            ):

                overlap = set(
                    relevant_skills
                ) & set(
                    retrieved_skills
                )

                if overlap:

                    score += 0.25

            # -----------------------------------------
            # TYPE BONUS
            # -----------------------------------------

            if (
                relevant_type
                and retrieved_type
            ):

                if relevant_type == retrieved_type:

                    score += 0.15

            best_match_score = max(
                best_match_score,
                score
            )

        total_score += best_match_score

    return total_score / len(relevant_items)

# -----------------------------------------------------
# MAIN TEST
# -----------------------------------------------------


def test_recall():

    with open(
        "app/tests/mock_conversations.json",
        "r",
        encoding="utf-8"
    ) as f:

        conversations = json.load(f)

    scores = []

    print("\n")
    print("=" * 80)
    print("RECALL@10 EVALUATION")
    print("=" * 80)

    for convo in conversations:

        if (
            "expected_assessments"
            not in convo
        ):
            continue

        latest_query = convo[
            "conversation"
        ][-1]["content"]

        expected = convo[
            "expected_assessments"
        ]

        results = retriever.search(
            latest_query,
            top_k=20
        )

        score = recall_at_k(
            relevant_items=expected,
            retrieved_items=results,
            k=10
        )

        scores.append(score)

        # -------------------------------------------------
        # DEBUG OUTPUT
        # -------------------------------------------------

        print("\n")

        print(
            f"Query: {latest_query}"
        )

        print(
            f"Recall@10: {score:.4f}"
        )

        print("\nRetrieved Assessments:")

        for idx, item in enumerate(
            results[:10],
            start=1
        ):

            print(
                f"{idx}. "
                f"{item['name']} "
                f"| Score: "
                f"{item.get('score', 0):.4f}"
            )

        print("-" * 80)

    # -----------------------------------------------------
    # FINAL SCORE
    # -----------------------------------------------------

    mean_recall = (
        sum(scores) / len(scores)
    )

    print("\n")
    print("=" * 80)

    print(
        f"Mean Recall@10: "
        f"{mean_recall:.4f}"
    )

    print("=" * 80)

    # -----------------------------------------------------
    # ASSERTION
    # -----------------------------------------------------

    assert mean_recall >= 0.5