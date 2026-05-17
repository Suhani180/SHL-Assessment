"""
Realistic recruiter interaction tests.
"""

import json

from app.core.intent_analyzer import (
    IntentAnalyzer
)

analyzer = IntentAnalyzer()


def test_mock_conversations():

    with open(
        "app/tests/mock_conversations.json",
        "r"
    ) as f:

        conversations = json.load(f)

    for convo in conversations:

        result = analyzer.analyze(
            convo["conversation"]
        )

        expected = convo[
            "expected_behavior"
        ]

        if expected == (
            "clarification_then_recommendation"
        ):

            assert result["action"] in [
                "clarify",
                "recommend"
            ]

        elif expected == "refinement":

            assert result["action"] == "refine"

        elif expected == "comparison":

            assert result["action"] == "compare"