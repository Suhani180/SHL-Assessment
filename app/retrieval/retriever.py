# app/retrieval/retriever.py

"""
Production-grade semantic retriever for SHL assessments.

Optimized for:
- Higher Recall@10
- Recruiter-style semantic retrieval
- Hybrid semantic + keyword boosting
- Query expansion
- Skill-aware ranking
- SHL-only grounded recommendations
"""

import json
import logging
import os
from typing import Dict, List, Optional

from app.retrieval.embedder import EmbeddingGenerator
from app.retrieval.faiss_index import FAISSIndexManager

logger = logging.getLogger(__name__)


class SHLRetriever:

    def __init__(
        self,
        catalog_path: str,
        index_path: str,
        metadata_path: str,
        embedding_model: str = (
            "sentence-transformers/all-MiniLM-L6-v2"
        )
    ):

        self.catalog_path = catalog_path

        self.embedder = EmbeddingGenerator(
            model_name=embedding_model
        )

        self.embedding_dimension = 384

        self.index_manager = FAISSIndexManager(
            dimension=self.embedding_dimension,
            index_path=index_path,
            metadata_path=metadata_path
        )

    # -----------------------------------------------------
    # LOAD CATALOG
    # -----------------------------------------------------

    def load_catalog(self) -> List[Dict]:

        if not os.path.exists(self.catalog_path):

            raise FileNotFoundError(
                f"Catalog file not found: "
                f"{self.catalog_path}"
            )

        with open(
            self.catalog_path,
            "r",
            encoding="utf-8"
        ) as f:

            catalog = json.load(f)

        logger.info(
            f"Loaded {len(catalog)} SHL assessments."
        )

        return catalog

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    def validate_catalog_item(
        self,
        item: Dict
    ) -> bool:

        required_fields = [
            "name",
            "description",
            "url"
        ]

        for field in required_fields:

            if not item.get(field):
                return False

        if "shl.com" not in item["url"].lower():
            return False

        return True

    # -----------------------------------------------------
    # QUERY EXPANSION
    # -----------------------------------------------------

    def expand_query(
        self,
        query: str
    ) -> str:
        """
        Expand recruiter-style queries.
        """

        query_lower = query.lower()

        expansions = []

        expansion_map = {

            "backend": [
                "backend developer",
                "software engineer",
                "api development"
            ],

            "frontend": [
                "frontend developer",
                "ui developer",
                "javascript"
            ],

            "java": [
                "java developer",
                "spring boot",
                "backend programming"
            ],

            "python": [
                "python developer",
                "automation",
                "backend programming"
            ],

            "leadership": [
                "people management",
                "team management",
                "managerial hiring"
            ],

            "communication": [
                "stakeholder management",
                "soft skills",
                "behavioral skills"
            ],

            "personality": [
                "behavioral assessment",
                "workplace behavior"
            ],

            "developer": [
                "technical hiring",
                "coding assessment"
            ]
        }

        for keyword, related_terms in expansion_map.items():

            if keyword in query_lower:

                expansions.extend(related_terms)

        expanded_query = (
            query + " " + " ".join(expansions)
        )

        return expanded_query

    # -----------------------------------------------------
    # PREPARE DOCUMENT TEXT
    # -----------------------------------------------------

    def prepare_document_text(
        self,
        item: Dict
    ) -> str:
        """
        Create enriched semantic representation.
        """

        name = item.get("name", "")

        description = item.get(
            "description",
            ""
        )

        skills = item.get(
            "skills",
            []
        )

        test_type = item.get(
            "test_type",
            ""
        )

        duration = item.get(
            "duration",
            ""
        )

        if isinstance(skills, list):
            skills_text = " ".join(skills)
        else:
            skills_text = str(skills)

        combined_text = (
            f"{name} {description} {skills_text}"
        ).lower()

        semantic_tags = []

        # -----------------------------------------
        # DYNAMIC TAGGING
        # -----------------------------------------

        if any(
            term in combined_text
            for term in [
                "java",
                "programming",
                "coding"
            ]
        ):

            semantic_tags.extend([
                "software engineer",
                "backend developer",
                "coding assessment",
                "technical hiring"
            ])

        if any(
            term in combined_text
            for term in [
                "leadership",
                "manager",
                "management"
            ]
        ):

            semantic_tags.extend([
                "leadership hiring",
                "people management",
                "managerial assessment"
            ])

        if any(
            term in combined_text
            for term in [
                "personality",
                "behavior",
                "opq"
            ]
        ):

            semantic_tags.extend([
                "behavioral assessment",
                "personality evaluation",
                "workplace behavior"
            ])

        if any(
            term in combined_text
            for term in [
                "communication",
                "stakeholder"
            ]
        ):

            semantic_tags.extend([
                "communication skills",
                "stakeholder management",
                "soft skills"
            ])

        semantic_text = f"""
        SHL Assessment:
        {name}

        Description:
        {description}

        Skills:
        {skills_text}

        Semantic Tags:
        {' '.join(semantic_tags)}

        Test Type:
        {test_type}

        Duration:
        {duration}
        """

        return semantic_text.strip()

    # -----------------------------------------------------
    # BUILD INDEX
    # -----------------------------------------------------

    def build(self) -> None:

        logger.info(
            "Building SHL retrieval index..."
        )

        catalog = self.load_catalog()

        catalog = [

            item for item in catalog

            if self.validate_catalog_item(item)
        ]

        texts = [

            self.prepare_document_text(item)

            for item in catalog
        ]

        logger.info(
            f"Generating embeddings for "
            f"{len(texts)} assessments..."
        )

        embeddings = self.embedder.embed_texts(
            texts
        )

        self.index_manager.build_index(
            embeddings=embeddings,
            metadata=catalog
        )

        self.index_manager.save()

        logger.info(
            "Retrieval index built successfully."
        )

    # -----------------------------------------------------
    # LOAD INDEX
    # -----------------------------------------------------

    def load(self) -> None:

        self.index_manager.load()

    # -----------------------------------------------------
    # FILTER DUPLICATES
    # -----------------------------------------------------

    def filter_duplicates(
        self,
        results: List[Dict]
    ) -> List[Dict]:

        unique_results = []

        seen_urls = set()

        for item in results:

            url = item.get("url", "")

            if url not in seen_urls:

                seen_urls.add(url)

                unique_results.append(item)

        return unique_results

    # -----------------------------------------------------
    # BOOST SCORES
    # -----------------------------------------------------

    def boost_scores(
        self,
        query: str,
        results: List[Dict]
    ) -> List[Dict]:

        query_lower = query.lower()

        for item in results:

            boost = 0.0

            combined_text = (
                item.get("name", "")
                + " "
                + item.get("description", "")
                + " "
                + " ".join(
                    item.get("skills", [])
                )
            ).lower()

            important_terms = [

                "java",
                "python",
                "leadership",
                "communication",
                "personality",
                "backend",
                "frontend",
                "developer",
                "coding"
            ]

            for term in important_terms:

                if (
                    term in query_lower
                    and term in combined_text
                ):

                    boost += 0.10

            item["score"] = float(
                item["score"]
            ) + boost

        return results

    # -----------------------------------------------------
    # NORMALIZE SCORES
    # -----------------------------------------------------

    def normalize_scores(
        self,
        results: List[Dict]
    ) -> List[Dict]:

        if not results:
            return results

        scores = [

            item["score"]

            for item in results
        ]

        max_score = max(scores)

        min_score = min(scores)

        for item in results:

            if max_score == min_score:

                normalized = 1.0

            else:

                normalized = (
                    (item["score"] - min_score)
                    / (max_score - min_score)
                )

            item["normalized_score"] = round(
                normalized,
                4
            )

        return results

    # -----------------------------------------------------
    # FORMAT RESULTS
    # -----------------------------------------------------

    def format_results(
        self,
        results: List[Dict]
    ) -> List[Dict]:

        formatted = []

        for item in results:

            formatted.append({

                "name": item.get("name", ""),

                "url": item.get("url", ""),

                "test_type": item.get(
                    "test_type",
                    ""
                ),

                "description": item.get(
                    "description",
                    ""
                ),

                "skills": item.get(
                    "skills",
                    []
                ),

                "duration": item.get(
                    "duration",
                    ""
                ),

                "score": round(
                    item.get("score", 0.0),
                    4
                ),

                "normalized_score": item.get(
                    "normalized_score",
                    0.0
                )
            })

        return formatted

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: float = 0.08
    ) -> List[Dict]:

        logger.info(
            f"Searching SHL catalog: {query}"
        )

        # -----------------------------------------
        # QUERY EXPANSION
        # -----------------------------------------

        expanded_query = self.expand_query(
            query
        )

        # -----------------------------------------
        # EMBEDDING
        # -----------------------------------------

        query_embedding = (
            self.embedder.embed_query(
                expanded_query
            )
        )

        # -----------------------------------------
        # INITIAL RETRIEVAL
        # -----------------------------------------

        results = self.index_manager.search(
            query_embedding=query_embedding,
            top_k=top_k * 3
        )

        # -----------------------------------------
        # SCORE FILTERING
        # -----------------------------------------

        filtered_results = [

            item for item in results

            if item.get("score", 0.0)
            >= score_threshold
        ]

        # -----------------------------------------
        # REMOVE DUPLICATES
        # -----------------------------------------

        filtered_results = (
            self.filter_duplicates(
                filtered_results
            )
        )

        # -----------------------------------------
        # BOOST SCORES
        # -----------------------------------------

        filtered_results = (
            self.boost_scores(
                expanded_query,
                filtered_results
            )
        )

        # -----------------------------------------
        # SORT
        # -----------------------------------------

        filtered_results = sorted(

            filtered_results,

            key=lambda x: x["score"],

            reverse=True
        )

        # -----------------------------------------
        # NORMALIZE
        # -----------------------------------------

        filtered_results = (
            self.normalize_scores(
                filtered_results
            )
        )

        # -----------------------------------------
        # FORMAT
        # -----------------------------------------

        formatted_results = (
            self.format_results(
                filtered_results[:top_k]
            )
        )

        logger.info(
            f"Retrieved "
            f"{len(formatted_results)} "
            f"SHL assessments."
        )

        return formatted_results