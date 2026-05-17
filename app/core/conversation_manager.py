import logging
from typing import Dict, List

from app.core.intent_analyzer import (
    IntentAnalyzer
)

from app.core.prompt_builder import (
    PromptBuilder
)

from app.core.refusal_handler import (
    RefusalHandler
)

from app.core.comparison_engine import (
    ComparisonEngine
)

from app.core.recommendation_engine import (
    RecommendationEngine
)

logger = logging.getLogger(__name__)


class ConversationManager:

    def __init__(
        self,
        retriever,
        llm_client
    ):

        self.retriever = retriever

        self.llm_client = llm_client

        self.intent_analyzer = IntentAnalyzer()

        self.prompt_builder = PromptBuilder()

        self.refusal_handler = RefusalHandler()

        self.comparison_engine = ComparisonEngine(
            retriever=retriever,
            llm_client=llm_client
        )

        self.recommendation_engine = (
            RecommendationEngine(
                retriever=retriever,
                llm_client=llm_client
            )
        )

    # -------------------------------------------------
    # MAIN HANDLER
    # -------------------------------------------------

    async def handle_conversation(
        self,
        messages
    ) -> Dict:

        try:

            if not messages:

                return self.build_response(
                    reply=(
                        "Please provide hiring "
                        "requirements."
                    ),
                    recommendations=[],
                    end=False
                )

            latest_user_message = (
                self.get_latest_user_message(
                    messages
                )
            )

            # -------------------------------------
            # REFUSAL CHECK
            # -------------------------------------

            refusal_response = (
                self.refusal_handler
                .check_refusal(
                    latest_user_message
                )
            )

            if refusal_response:

                return self.build_response(
                    reply=refusal_response,
                    recommendations=[],
                    end=False
                )

            # -------------------------------------
            # CONVERT TO DICTS
            # -------------------------------------

            message_dicts = [

                {
                    "role": msg.role,
                    "content": msg.content
                }

                for msg in messages
            ]

            # -------------------------------------
            # ANALYZE INTENT
            # -------------------------------------

            analysis = (
                self.intent_analyzer.analyze(
                    message_dicts
                )
            )

            logger.info(
                f"Analysis: {analysis}"
            )

            action = analysis["action"]

            # -------------------------------------
            # CLARIFICATION
            # -------------------------------------

            if action == "clarify":

                prompt = (
                    self.prompt_builder
                    .build_clarification_prompt(
                        analysis,
                        message_dicts
                    )
                )

                reply = (
                    self.llm_client.generate(
                        prompt
                    )
                )

                return self.build_response(
                    reply=reply,
                    recommendations=[],
                    end=False
                )

            # -------------------------------------
            # COMPARISON
            # -------------------------------------

            elif action == "compare":

                comparison_reply = (
                    self.comparison_engine.compare(
                        analysis
                    )
                )

                return self.build_response(
                    reply=comparison_reply,
                    recommendations=[],
                    end=False
                )

            # -------------------------------------
            # RECOMMENDATIONS
            # -------------------------------------

            recommendations = (
                self.recommendation_engine
                .generate_recommendations(
                    analysis=analysis,
                    messages=message_dicts
                )
            )

            if not recommendations:

                return self.build_response(
                    reply=(
                        "I could not find suitable "
                        "SHL assessments."
                    ),
                    recommendations=[],
                    end=False
                )

            prompt = (
                self.prompt_builder
                .build_recommendation_prompt(
                    analysis,
                    recommendations
                )
            )

            reply = self.llm_client.generate(
                prompt
            )

            return self.build_response(
                reply=reply,
                recommendations=recommendations,
                end=False
            )

        except Exception as e:

            import traceback

            print("\n\n========== ERROR ==========\n")

            traceback.print_exc()

            print("\n===========================\n")

            return self.build_response(
                reply=f"DEBUG ERROR: {str(e)}",
                recommendations=[],
                end=False
            )

    # -------------------------------------------------
    # RESPONSE BUILDER
    # -------------------------------------------------

    def build_response(
        self,
        reply: str,
        recommendations: List[Dict],
        end: bool
    ) -> Dict:

        cleaned = []

        for item in recommendations[:10]:

            cleaned.append({

                "name": item.get(
                    "name",
                    ""
                ),

                "url": item.get(
                    "url",
                    ""
                ),

                "test_type": item.get(
                    "test_type",
                    ""
                )
            })

        return {

            "reply": reply,

            "recommendations": cleaned,

            "end_of_conversation": end
        }

    # -------------------------------------------------
    # GET LATEST USER MESSAGE
    # -------------------------------------------------

    def get_latest_user_message(
        self,
        messages
    ) -> str:

        for msg in reversed(messages):

            if msg.role == "user":

                return msg.content

        return ""