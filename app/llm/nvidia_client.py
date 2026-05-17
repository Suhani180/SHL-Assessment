# app/llm/nvidia_client.py

import os

from dotenv import load_dotenv

from openai import OpenAI


# -----------------------------------------------------
# LOAD ENV
# -----------------------------------------------------

load_dotenv()


class NvidiaClient:

    def __init__(self):

        api_key = os.getenv(
            "NVIDIA_API_KEY"
        )

        if not api_key:

            raise ValueError(
                "Missing NVIDIA_API_KEY"
            )

        print(
            "NVIDIA API loaded successfully."
        )

        self.client = OpenAI(

            base_url="https://integrate.api.nvidia.com/v1",

            api_key=api_key
        )

        self.model_name = os.getenv(
            "MODEL_NAME",
            "meta/llama-3.1-8b-instruct"
        )

    # -------------------------------------------------
    # GENERATE
    # -------------------------------------------------

    def generate(
        self,
        prompt: str
    ) -> str:

        try:
            print("Generating NVIDIA response...")
            completion = (
                self.client.chat.completions.create(

                    model=self.model_name,

                    messages=[

                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.2,

                    max_tokens=512
                )
            )
            print("NVIDIA response received.")
            return (
                completion
                .choices[0]
                .message
                .content
                .strip()
            )

        except Exception as e:

            print(
                f"NVIDIA generation error: {e}"
            )

            raise e