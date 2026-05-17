# app/retrieval/faiss_index.py

"""
FAISS index manager.
Handles:
- index creation
- persistence
- loading
- similarity search
"""

import faiss
import pickle
import numpy as np
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class FAISSIndexManager:

    def __init__(
        self,
        dimension: int,
        index_path: str,
        metadata_path: str
    ):

        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = metadata_path

        self.index = faiss.IndexFlatIP(dimension)

        self.metadata = []

    # -----------------------------------------------------
    # BUILD INDEX
    # -----------------------------------------------------

    def build_index(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict]
    ) -> None:
        """
        Build FAISS index.
        """

        logger.info("Building FAISS index...")

        self.index.add(embeddings.astype(np.float32))

        self.metadata = metadata

        logger.info(
            f"Indexed {len(metadata)} assessments."
        )

    # -----------------------------------------------------
    # SAVE INDEX
    # -----------------------------------------------------

    def save(self) -> None:
        """
        Save index + metadata locally.
        """

        logger.info("Saving FAISS index...")

        faiss.write_index(
            self.index,
            self.index_path
        )

        with open(
            self.metadata_path,
            "wb"
        ) as f:

            pickle.dump(self.metadata, f)

        logger.info("Index saved successfully.")

    # -----------------------------------------------------
    # LOAD INDEX
    # -----------------------------------------------------

    def load(self) -> None:
        """
        Load saved FAISS index.
        """

        logger.info("Loading FAISS index...")

        if not os.path.exists(self.index_path):
            raise FileNotFoundError(
                f"Missing index file: {self.index_path}"
            )

        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(
                f"Missing metadata file: {self.metadata_path}"
            )

        self.index = faiss.read_index(
            self.index_path
        )

        with open(
            self.metadata_path,
            "rb"
        ) as f:

            self.metadata = pickle.load(f)

        logger.info(
            f"Loaded {len(self.metadata)} indexed assessments."
        )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Perform similarity search.
        """

        query_embedding = np.expand_dims(
            query_embedding,
            axis=0
        ).astype(np.float32)

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx < 0:
                continue

            item = self.metadata[idx].copy()

            item["score"] = float(score)

            results.append(item)

        return results