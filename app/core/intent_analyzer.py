# app/core/intent_analyzer.py

from typing import Dict, List


class IntentAnalyzer:

    def analyze(
        self,
        messages
    ) -> Dict:

        user_messages = []

        # -----------------------------------------
        # EXTRACT USER CONTENT SAFELY
        # -----------------------------------------

        for m in messages:

            # Pydantic object
            if hasattr(m, "role"):

                if m.role == "user":

                    user_messages.append(
                        m.content
                    )

            # Dictionary fallback
            elif isinstance(m, dict):

                if m.get("role") == "user":

                    user_messages.append(
                        m.get("content", "")
                    )

        full_context = " ".join(
            user_messages
        ).lower()

        latest_message = (
            user_messages[-1].lower()
            if user_messages
            else ""
        )

        # -----------------------------------------
        # COMPARISON
        # -----------------------------------------

        if any(
            word in latest_message
            for word in [
                "compare",
                "difference",
                "vs",
                "versus"
            ]
        ):

            return {

                "action": "compare",

                "query": latest_message
            }

        # -----------------------------------------
        # REFINEMENT
        # -----------------------------------------

        refinement_keywords = [

            "also",
            "include",
            "add",
            "actually",
            "change"
        ]

        if any(
            word in latest_message
            for word in refinement_keywords
        ):

            return {

                "action": "refine",

                "query": full_context
            }

        # -----------------------------------------
        # CLARIFICATION
        # -----------------------------------------

        vague_queries = [

            "i need assessment",
            "need assessment",
            "hiring",
            "need hiring test"
        ]

        if (
            latest_message.strip()
            in vague_queries
            or len(latest_message.split()) < 4
        ):

            return {

                "action": "clarify",

                "query": latest_message
            }

        # -----------------------------------------
        # RECOMMENDATION
        # -----------------------------------------

        return {

            "action": "recommend",

            "query": full_context
        }