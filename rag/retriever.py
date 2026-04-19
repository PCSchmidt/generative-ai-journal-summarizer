"""Retriever: embeds queries with sentence-transformers and searches the journal store."""

from sentence_transformers import SentenceTransformer

from .store import JournalStore


class JournalRetriever:
    """Wraps embedding model + journal store for retrieval-augmented generation."""

    def __init__(self, store: JournalStore, model_name: str = "all-MiniLM-L6-v2"):
        self.store = store
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str):
        """Return a numpy vector for a single text string."""
        return self.model.encode(text, convert_to_numpy=True)

    def ingest(self, text: str, user_id: str | None = None) -> dict:
        """Embed and store a new journal entry. Returns the stored record."""
        embedding = self.embed(text)
        return self.store.add_entry(text, embedding, user_id=user_id)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Embed the query and return the top-k most similar past entries."""
        embedding = self.embed(query)
        return self.store.search(embedding, top_k=top_k)
