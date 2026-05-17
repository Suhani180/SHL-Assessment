# app/retrieval/embedder.py

"""
Embedding generator for SHL assessment catalog.
Uses sentence-transformers/all-MiniLM-L6-v2
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Handles text embedding generation.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        logger.info(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)

    def embed_texts(
        self,
        texts: List[str]
    ) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        """

        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings

    def embed_query(
        self,
        query: str
    ) -> np.ndarray:
        """
        Generate embedding for a single query.
        """

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding