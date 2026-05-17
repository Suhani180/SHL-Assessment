from typing import Dict, List


class RecommendationEngine:

    def __init__(
        self,
        retriever,
        llm_client
    ):

        self.retriever = retriever

        self.llm_client = llm_client

    # -------------------------------------------------
    # GENERATE RECOMMENDATIONS
    # -------------------------------------------------

    def generate_recommendations(
        self,
        analysis: Dict,
        messages: List[Dict]
    ) -> List[Dict]:

        query = analysis["query"]

        results = self.retriever.search(
            query=query,
            top_k=10
        )

        grounded_results = []

        for item in results:

            grounded_results.append({

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
                ),

                "description": item.get(
                    "description",
                    ""
                ),

                "skills": item.get(
                    "skills",
                    []
                )
            })

        return grounded_results