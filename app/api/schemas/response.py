"""
Response schemas.
"""

from typing import List

from pydantic import BaseModel


class Recommendation(BaseModel):

    name: str

    url: str

    test_type: str


class ChatResponse(BaseModel):

    reply: str

    recommendations: List[Recommendation]

    end_of_conversation: bool