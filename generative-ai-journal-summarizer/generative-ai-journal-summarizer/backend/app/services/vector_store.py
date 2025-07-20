from typing import List, Dict
import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from ..core.config import settings

class VectorStoreService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDINGS_MODEL)
        self.vector_store = None
        self.load_vector_store()
    
    def load_vector_store(self):
        """Load existing vector store or create new one"""
        try:
            if os.path.exists(settings.VECTOR_DB_PATH):
                self.vector_store = FAISS.load_local(settings.VECTOR_DB_PATH, self.embeddings)
            else:
                # Create empty vector store
                self.vector_store = FAISS.from_texts([""], self.embeddings)
        except Exception as e:
            print(f"Vector store initialization failed: {e}")
    
    async def add_documents(self, texts: List[str], metadata: List[Dict] = None):
        """Add documents to vector store"""
        try:
            if metadata is None:
                metadata = [{}] * len(texts)
            
            # Split texts if they're too long
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            split_texts = []
            split_metadata = []
            
            for i, text in enumerate(texts):
                chunks = text_splitter.split_text(text)
                split_texts.extend(chunks)
                split_metadata.extend([metadata[i]] * len(chunks))
            
            # Add to vector store
            self.vector_store.add_texts(split_texts, split_metadata)
            self.save_vector_store()
            
        except Exception as e:
            print(f"Failed to add documents: {e}")
    
    async def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        try:
            docs = self.vector_store.similarity_search_with_score(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                }
                for doc, score in docs
            ]
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def save_vector_store(self):
        """Save vector store to disk"""
        try:
            os.makedirs(os.path.dirname(settings.VECTOR_DB_PATH), exist_ok=True)
            self.vector_store.save_local(settings.VECTOR_DB_PATH)
        except Exception as e:
            print(f"Failed to save vector store: {e}")

# Global vector store instance
vector_store_service = VectorStoreService()
