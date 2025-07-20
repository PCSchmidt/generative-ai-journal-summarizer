from typing import List, Dict, Optional
import os
from datetime import datetime
# from langchain.llms import HuggingFacePipeline
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.text_splitter import CharacterTextSplitter
from ..core.config import settings

class AIService:
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.llm = None
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize AI services"""
        try:
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDINGS_MODEL
            )
            
            # Load vector store if exists
            vector_store_path = settings.VECTOR_DB_PATH
            if os.path.exists(vector_store_path):
                self.vector_store = FAISS.load_local(vector_store_path, self.embeddings)
            
            # Initialize LLM (start with HuggingFace free tier)
            self.initialize_llm()
            
        except Exception as e:
            print(f"AI service initialization warning: {e}")
    
    def initialize_llm(self):
        """Initialize language model"""
        if settings.OPENAI_API_KEY:
            from langchain.llms import OpenAI
            self.llm = OpenAI(openai_api_key=settings.OPENAI_API_KEY)
        elif settings.HUGGINGFACE_API_KEY:
            # Use HuggingFace Inference API
            self.llm = HuggingFacePipeline.from_model_id(
                model_id="microsoft/DialoGPT-medium",
                task="text-generation",
                model_kwargs={"temperature": 0.7, "max_length": 512}
            )
        else:
            print("No AI API keys found. Using fallback responses.")
    
    async def process_text(self, text: str, task_type: str = "analyze") -> Dict:
        """Process text with AI"""
        if not self.llm:
            return self._fallback_response(text, task_type)
        
        try:
            prompt_template = self._get_prompt_template(task_type)
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = await chain.arun(text=text)
            return self._parse_response(result, task_type)
        except Exception as e:
            print(f"AI processing failed: {e}")
            return self._fallback_response(text, task_type)
    
    def _get_prompt_template(self, task_type: str) -> PromptTemplate:
        """Get prompt template for specific task"""
        templates = {
            "analyze": PromptTemplate(
                input_variables=["text"],
                template="Analyze the following text and provide insights:\n\n{text}\n\nAnalysis:"
            ),
            "summarize": PromptTemplate(
                input_variables=["text"],
                template="Summarize the following text concisely:\n\n{text}\n\nSummary:"
            ),
            "generate": PromptTemplate(
                input_variables=["text"],
                template="Based on this input, generate creative content:\n\n{text}\n\nGenerated content:"
            )
        }
        return templates.get(task_type, templates["analyze"])
    
    def _parse_response(self, response: str, task_type: str) -> Dict:
        """Parse AI response into structured format"""
        return {
            "result": response.strip(),
            "task_type": task_type,
            "confidence": 0.8,
            "metadata": {
                "model": "ai_service",
                "timestamp": str(datetime.utcnow())
            }
        }
    
    def _fallback_response(self, text: str, task_type: str) -> Dict:
        """Fallback response when AI is unavailable"""
        word_count = len(text.split())
        
        fallbacks = {
            "analyze": f"Text analysis: {word_count} words detected. Content appears to contain meaningful information.",
            "summarize": f"Summary: Text with {word_count} words covering various topics.",
            "generate": f"Generated content based on {word_count} word input would be created here."
        }
        
        return {
            "result": fallbacks.get(task_type, "AI processing result would appear here."),
            "task_type": task_type,
            "confidence": 0.5,
            "metadata": {
                "model": "fallback",
                "timestamp": str(datetime.utcnow())
            }
        }
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts"""
        if not self.embeddings:
            return []
        
        try:
            return await self.embeddings.aembed_documents(texts)
        except Exception as e:
            print(f"Embedding creation failed: {e}")
            return []
    
    async def similarity_search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar content in vector store"""
        if not self.vector_store:
            return []
        
        try:
            docs = await self.vector_store.asimilarity_search(query, k=k)
            return [{"content": doc.page_content, "score": doc.metadata.get("score", 0)} for doc in docs]
        except Exception as e:
            print(f"Similarity search failed: {e}")
            return []

# Global AI service instance
ai_service = AIService()
