# app/utils/prompt_loader.py

"""
Prompt loading utility for SHL Conversational Recommender.

Features:
- load prompt templates from text files
- validate file existence
- safe formatting support
- caching support
- production-grade error handling
"""

import os
import logging
from functools import lru_cache
from typing import Dict

logger = logging.getLogger(__name__)


class PromptLoader:
    """
    Utility class for loading and formatting prompts.
    """

    def __init__(
        self,
        base_path: str = "app/llm/prompts"
    ):

        self.base_path = base_path

    # -----------------------------------------------------
    # LOAD PROMPT FILE
    # -----------------------------------------------------

    @lru_cache(maxsize=32)
    def load_prompt(
        self,
        filename: str
    ) -> str:
        """
        Load prompt text from file.

        Uses caching to avoid repeated disk reads.
        """

        try:

            prompt_path = os.path.join(
                self.base_path,
                filename
            )

            if not os.path.exists(prompt_path):

                raise FileNotFoundError(
                    f"Prompt file not found: "
                    f"{prompt_path}"
                )

            with open(
                prompt_path,
                "r",
                encoding="utf-8"
            ) as f:

                content = f.read().strip()

            if not content:

                raise ValueError(
                    f"Prompt file is empty: "
                    f"{prompt_path}"
                )

            logger.info(
                f"Loaded prompt: {filename}"
            )

            return content

        except Exception as e:

            logger.exception(
                f"Failed to load prompt "
                f"{filename}: {e}"
            )

            raise

    # -----------------------------------------------------
    # FORMAT PROMPT
    # -----------------------------------------------------

    def format_prompt(
        self,
        filename: str,
        variables: Dict
    ) -> str:
        """
        Load + format prompt template.
        """

        try:

            template = self.load_prompt(
                filename
            )

            formatted_prompt = template.format(
                **variables
            )

            return formatted_prompt

        except KeyError as e:

            logger.exception(
                f"Missing template variable: {e}"
            )

            raise

        except Exception as e:

            logger.exception(
                f"Prompt formatting error: {e}"
            )

            raise

    # -----------------------------------------------------
    # LIST AVAILABLE PROMPTS
    # -----------------------------------------------------

    def list_prompts(self):
        """
        Return available prompt files.
        """

        try:

            files = []

            for file in os.listdir(
                self.base_path
            ):

                if file.endswith(".txt"):

                    files.append(file)

            return sorted(files)

        except Exception as e:

            logger.exception(
                f"Error listing prompts: {e}"
            )

            return []

    # -----------------------------------------------------
    # VALIDATE PROMPTS
    # -----------------------------------------------------

    def validate_prompts(self):
        """
        Validate all prompt files.
        """

        required_prompts = [

            "system_prompt.txt",

            "clarification_prompt.txt",

            "recommendation_prompt.txt",

            "refinement_prompt.txt",

            "comparison_prompt.txt",

            "refusal_prompt.txt"
        ]

        missing = []

        for prompt_file in required_prompts:

            path = os.path.join(
                self.base_path,
                prompt_file
            )

            if not os.path.exists(path):

                missing.append(prompt_file)

        if missing:

            raise FileNotFoundError(
                f"Missing prompt files: {missing}"
            )

        logger.info(
            "All prompt files validated."
        )

        return True


# ---------------------------------------------------------
# GLOBAL INSTANCE
# ---------------------------------------------------------

prompt_loader = PromptLoader()