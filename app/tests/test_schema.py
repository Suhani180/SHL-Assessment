"""
Schema compliance tests.
"""

from app.api.schemas.response import (
    ChatResponse
)


def test_response_schema():

    response = {

        "reply": "Example reply",

        "recommendations": [
            {
                "name": "Java 8 (New)",
                "url": "https://www.shl.com/",
                "test_type": "K"
            }
        ],

        "end_of_conversation": False
    }

    validated = ChatResponse(**response)

    assert validated.reply
    assert isinstance(
        validated.recommendations,
        list
    )