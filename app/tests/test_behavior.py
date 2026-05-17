"""
Behavior testing.
"""

from app.core.intent_analyzer import (
    IntentAnalyzer
)

analyzer = IntentAnalyzer()


def test_vague_query():

    messages = [

        {
            "role": "user",
            "content": "I need assessment"
        }
    ]

    result = analyzer.analyze(messages)

    assert result["action"] == "clarify"


def test_refinement():

    messages = [

        {
            "role": "user",
            "content": "Hiring Python developer"
        },

        {
            "role": "user",
            "content": (
                "Actually include "
                "personality tests"
            )
        }
    ]

    result = analyzer.analyze(messages)

    assert result["action"] == "refine"


def test_comparison():

    messages = [

        {
            "role": "user",
            "content": (
                "Compare OPQ and GSA"
            )
        }
    ]

    result = analyzer.analyze(messages)

    assert result["action"] == "compare"