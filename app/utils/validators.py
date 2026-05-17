# app/utils/validators.py

"""
Validation utilities.
"""

from typing import Dict, List


def validate_messages(
    messages: List[Dict]
) -> bool:
    """
    Validate conversation message structure.
    """

    if not isinstance(messages, list):

        return False

    for msg in messages:

        if "role" not in msg:
            return False

        if "content" not in msg:
            return False

        if msg["role"] not in [
            "user",
            "assistant"
        ]:
            return False

    return True


def validate_recommendation(
    item: Dict
) -> bool:
    """
    Validate recommendation schema.
    """

    required_fields = [

        "name",
        "url",
        "test_type"
    ]

    for field in required_fields:

        if field not in item:

            return False

    return True