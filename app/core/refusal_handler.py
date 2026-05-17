# app/core/refusal_handler.py

"""
Prompt injection + off-topic protection.
"""


class RefusalHandler:

    def __init__(self):

        self.blocked_patterns = [

            "ignore previous instructions",

            "ignore instructions",

            "bypass system",

            "act as",

            "jailbreak",

            "salary",

            "legal advice",

            "politics",

            "competitor",

            "openai",

            "leetcode"
        ]

    def check_refusal(
        self,
        text: str
    ):

        text = text.lower()

        for pattern in self.blocked_patterns:

            if pattern in text:

                return (
                    "I can only assist with "
                    "SHL assessment recommendations "
                    "and comparisons."
                )

        return None