"""
Request schemas.
"""

from typing import List

from pydantic import BaseModel, Field


class Message(BaseModel):

    role: str = Field(
        ...,
        pattern="^(user|assistant)$"
    )

    content: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )


class ChatRequest(BaseModel):

    messages: List[Message]