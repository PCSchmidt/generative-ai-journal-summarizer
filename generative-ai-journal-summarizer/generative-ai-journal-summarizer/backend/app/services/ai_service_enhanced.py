from typing import List, Dict, Optional
import os
from datetime import datetime

class AIService:
    def __init__(self):
        self.llm = None
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize AI services"""
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if groq_api_key:
                print("🚀 Initializing Groq AI service...")
                from langchain_groq import ChatGroq
                self.llm = ChatGroq(
                    groq_api_key=groq_api_key,
                    model_name="llama3-8b-8192",  # Fast and capable model
                    temperature=0.3  # Low temperature for consistent results
                )
                print("✅ Groq AI service initialized successfully!")
            else:
                print("⚠️  No GROQ_API_KEY found. Using fallback responses.")
                self.llm = None
        except Exception as e:
            print(f"⚠️  AI service initialization failed: {e}. Using fallback responses.")
            self.llm = None
    
    async def process_text(self, text: str, task_type: str = "analyze") -> Dict:
        """Process text with AI"""
        if self.llm:
            try:
                return await self._ai_process(text, task_type)
            except Exception as e:
                print(f"AI processing error: {e}. Using fallback.")
                return self._fallback_response(text, task_type)
        else:
            return self._fallback_response(text, task_type)
    
    async def _ai_process(self, text: str, task_type: str) -> Dict:
        """Process text using real AI"""
        prompt = self._get_ai_prompt(text, task_type)
        
        try:
            # Use invoke instead of arun for newer LangChain versions
            response = self.llm.invoke(prompt)
            result = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "result": result.strip(),
                "task_type": task_type,
                "confidence": 0.9,  # High confidence for real AI
                "metadata": {
                    "model": "groq-llama3-8b",
                    "timestamp": datetime.utcnow().isoformat(),
                    "word_count": len(text.split())
                }
            }
        except Exception as e:
            print(f"AI processing error: {e}")
            raise e
    
    def _get_ai_prompt(self, text: str, task_type: str) -> str:
        """Get AI prompt based on task type"""
        prompts = {
            "analyze": f"""
Analyze this journal entry and provide insights about the person's thoughts, emotions, and experiences:

Journal Entry:
"{text}"

Please provide:
1. A brief summary of the main topics
2. The emotional tone and sentiment
3. Key themes or patterns you notice
4. Any insights about the person's mindset or situation

Keep your response concise but insightful.
""",
            "summarize": f"""
Summarize this journal entry in 2-3 sentences, capturing the main points and emotional tone:

Journal Entry:
"{text}"

Summary:
""",
            "sentiment": f"""
Analyze the emotional sentiment of this journal entry:

Journal Entry:
"{text}"

Provide:
1. Overall sentiment (positive/negative/neutral with percentage)
2. Main emotions detected
3. Emotional intensity level (1-10)
4. Brief explanation of the emotional patterns

Response:
""",
            "insights": f"""
Extract meaningful insights and patterns from this journal entry:

Journal Entry:
"{text}"

Provide insights about:
1. Personal growth indicators
2. Recurring themes or concerns
3. Decision-making patterns
4. Areas of focus or change
5. Potential action items or reflections

Insights:
"""
        }
        
        return prompts.get(task_type, prompts["analyze"])
    
    def _fallback_response(self, text: str, task_type: str) -> Dict:
        """Fallback response when AI is unavailable"""
        word_count = len(text.split())
        sentiment_words = ["happy", "joy", "excited", "love", "great", "amazing", "wonderful"]
        negative_words = ["sad", "angry", "frustrated", "worried", "tired", "stressed"]
        
        # Simple sentiment analysis
        text_lower = text.lower()
        positive_count = sum(1 for word in sentiment_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = 0.6
        elif negative_count > positive_count:
            sentiment = "negative" 
            confidence = 0.6
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        fallbacks = {
            "analyze": f"Journal Analysis ({word_count} words):\n\nThis entry shows {sentiment} sentiment and covers personal thoughts and experiences. The writing demonstrates self-reflection and awareness of current life situations. Key themes include daily activities, emotional states, and personal observations.",
            
            "summarize": f"Summary: This {word_count}-word journal entry reflects {sentiment} thoughts about personal experiences, daily life, and current emotions. The writing shows introspection and engagement with ongoing life situations.",
            
            "sentiment": f"Sentiment Analysis:\n- Overall: {sentiment.title()} ({int(confidence*100)}%)\n- Emotional tone: {sentiment} with moderate intensity\n- Word count: {word_count} words\n- Analysis: Basic keyword detection suggests {sentiment} emotional patterns",
            
            "insights": f"Key Insights:\n- Entry length: {word_count} words suggests {'detailed' if word_count > 50 else 'brief'} reflection\n- Emotional tone: {sentiment}\n- Self-awareness: Evidence of introspective thinking\n- Communication style: Personal and reflective\n- Engagement level: Active journaling indicates good self-care habits"
        }
        
        return {
            "result": fallbacks.get(task_type, fallbacks["analyze"]),
            "task_type": task_type,
            "confidence": confidence,
            "metadata": {
                "model": "fallback-enhanced",
                "timestamp": datetime.utcnow().isoformat(),
                "word_count": word_count,
                "sentiment": sentiment
            }
        }
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts (placeholder for future implementation)"""
        return []
    
    async def similarity_search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar content (placeholder for future implementation)"""
        return []

# Global AI service instance
ai_service = AIService()
