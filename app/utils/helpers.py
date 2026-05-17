# app/utils/helpers.py

"""
General helper utilities.
"""

from typing import List, Dict


def flatten_conversation(
    messages: List[Dict]
) -> str:
    """
    Convert conversation messages
    into a single text block.
    """

    lines = []

    for msg in messages:

        role = msg.get("role", "user")

        content = msg.get("content", "")

        lines.append(
            f"{role}: {content}"
        )

    return "\n".join(lines)


def safe_lower(text: str) -> str:
    """
    Lowercase safely.
    """

    if not text:
        return ""

    return text.lower().strip()


def deduplicate_by_key(
    items: List[Dict],
    key: str
) -> List[Dict]:
    """
    Remove duplicate dict items.
    """

    seen = set()

    unique = []

    for item in items:

        value = item.get(key)

        if value not in seen:

            seen.add(value)

            unique.append(item)

    return unique