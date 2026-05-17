import asyncio
import traceback

from fastapi import (
    APIRouter,
    Depends
)

from app.api.schemas.request import (
    ChatRequest
)

from app.api.schemas.response import (
    ChatResponse
)

from app.dependencies import (
    get_conversation_manager
)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest,
    conversation_manager=Depends(
        get_conversation_manager
    )
):

    try:

        response = await asyncio.wait_for(

            conversation_manager.handle_conversation(
                request.messages
            ),

            timeout=30
        )

        return response

    except Exception as e:

        print("\n\n========== API ERROR ==========\n")

        traceback.print_exc()

        print("\n===============================\n")

        return {
            "reply": f"DEBUG ERROR: {str(e)}",
            "recommendations": [],
            "end_of_conversation": False
        }