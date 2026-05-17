# app/retrieval/test_search.py

"""
Quick retrieval testing script.
"""

from app.retrieval.retriever import SHLRetriever

retriever = SHLRetriever(
    catalog_path="app/catalog/catalog.json",
    index_path="app/vector_store/faiss.index",
    metadata_path="app/vector_store/metadata.pkl"
)

retriever.load()

query = "Hiring a Java backend developer with stakeholder communication"

results = retriever.search(
    query=query,
    top_k=5
)

for idx, result in enumerate(results, start=1):

    print("\n")
    print("=" * 60)

    print(f"Rank #{idx}")
    print(f"Name: {result['name']}")
    print(f"Score: {result['score']:.4f}")
    print(f"URL: {result['url']}")
    print(f"Skills: {result.get('skills', [])}")