"""
Lazy-loaded dependency manager.
"""

from app.retrieval.retriever import SHLRetriever
from app.llm.nvidia_client import NvidiaClient
from app.core.conversation_manager import (
    ConversationManager
)

retriever = None
llm_client = None
conversation_manager = None


def get_conversation_manager():

    global retriever
    global llm_client
    global conversation_manager

    # Lazy loading
    if conversation_manager is None:

        retriever = SHLRetriever(
            catalog_path="app/catalog/catalog.json",
            index_path="app/vector_store/faiss.index",
            metadata_path="app/vector_store/metadata.pkl"
        )

        retriever.load()

        llm_client = NvidiaClient()

        conversation_manager = ConversationManager(
            retriever=retriever,
            llm_client=llm_client
        )

    return conversation_manager