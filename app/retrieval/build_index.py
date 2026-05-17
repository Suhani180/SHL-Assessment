# app/retrieval/build_index.py

"""
Build FAISS index from catalog.
Run once before starting API.
"""

from app.retrieval.retriever import SHLRetriever

CATALOG_PATH = "app/catalog/catalog.json"

INDEX_PATH = "app/vector_store/faiss.index"

METADATA_PATH = "app/vector_store/metadata.pkl"


def main():

    retriever = SHLRetriever(
        catalog_path=CATALOG_PATH,
        index_path=INDEX_PATH,
        metadata_path=METADATA_PATH
    )

    retriever.build()


if __name__ == "__main__":
    main()