from typing import List, Dict

class VectorStoreService:
    def __init__(self):
        pass
    
    async def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar content"""
        return []
    
    async def add_texts(self, texts: List[str]) -> bool:
        """Add texts to vector store"""
        return True

# Global vector store service instance
vector_store_service = VectorStoreService()
