import re


class ComparisonEngine:

    def __init__(
        self,
        retriever,
        llm_client
    ):

        self.retriever = retriever

        self.llm_client = llm_client

    # -------------------------------------------------
    # COMPARE ASSESSMENTS
    # -------------------------------------------------

    def compare(
        self,
        analysis
    ):

        query = analysis["query"]

        names = re.split(
            r"vs|versus|compare|difference between",
            query
        )

        names = [
            n.strip()
            for n in names
            if n.strip()
        ]

        if len(names) < 2:

            return (
                "Please specify two SHL "
                "assessments to compare."
            )

        result_1 = self.retriever.search(
            names[0],
            top_k=1
        )

        result_2 = self.retriever.search(
            names[1],
            top_k=1
        )

        if not result_1 or not result_2:

            return (
                "I could not find both SHL "
                "assessments for comparison."
            )

        assessment_1 = result_1[0]

        assessment_2 = result_2[0]

        prompt = f"""
Compare these SHL assessments.

Assessment 1:
{assessment_1}

Assessment 2:
{assessment_2}

Requirements:
- concise
- factual
- grounded only
- no hallucinations
"""

        return self.llm_client.generate(
            prompt
        )