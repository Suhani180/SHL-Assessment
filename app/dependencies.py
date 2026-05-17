"""
Dependency initialization layer.
"""

from app.retrieval.retriever import SHLRetriever
from app.llm.nvidia_client import NvidiaClient
from app.core.conversation_manager import ConversationManager

# Singleton services

retriever = None
llm_client = None
conversation_manager = None


def initialize_services():

    global retriever
    global llm_client
    global conversation_manager

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


def get_conversation_manager():
    return conversation_manager