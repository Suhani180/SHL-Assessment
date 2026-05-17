from app.retrieval.retriever import SHLRetriever

retriever = SHLRetriever(
    catalog_path="app/catalog/catalog.json",
    index_path="app/vector_store/faiss.index",
    metadata_path="app/vector_store/metadata.pkl"
)

retriever.load()

queries = [

    "Java backend developer with leadership skills",

    "Python developer with communication skills",

    "Personality assessment for managers"
]

for query in queries:

    print("\n")
    print("=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = retriever.search(
        query=query,
        top_k=10
    )

    for idx, r in enumerate(results, start=1):

        print(
            f"{idx}. "
            f"{r['name']} "
            f"| Score: {r['score']:.4f}"
        )

        print(
            f"Skills: {r.get('skills', [])}"
        )

        print(
            f"Type: {r.get('test_type', '')}"
        )

        print("-" * 50)