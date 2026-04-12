# Railway Production FastAPI Backend - AI Journal Summarizer
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import httpx
import random
from typing import Optional, List, Dict, Any

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Journal Summarizer API",
    version="1.0.0",
    description="AI-powered journal summarizer backend - Railway Production"
)

# Configure CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.vercel.app",
        "https://vercel.app", 
        "http://localhost:3000",
        "http://localhost:19006",
        "*"  # Temporary for testing - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response Models
class TextProcessRequest(BaseModel):
    text: str
    task_type: str = "sentiment"
    model: Optional[str] = "groq-llama3-8b"  # Default model

class TextProcessResponse(BaseModel):
    result: str
    task_type: str
    confidence: float
    metadata: dict

# Enhanced AI Service with Real Groq Integration
class EnhancedAIService:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.groq_base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.hf_base_url = "https://api-inference.huggingface.co/models"
        self.fallback_count = 0
        self.last_provider_errors: Dict[str, Dict[str, Any]] = {}
        
        # Debug: Log API key status
        print(f"🔑 API Keys Status:")
        print(f"   GROQ_API_KEY: {'✅ Present' if self.groq_api_key else '❌ Missing'}")
        print(f"   HUGGINGFACE_API_KEY: {'✅ Present' if self.hf_api_key else '❌ Missing'}")
        if self.hf_api_key:
            print(f"   HF Key format: {'✅ Valid' if self.hf_api_key.startswith('hf_') else '⚠️ Unusual format'}")
        
        # Available models with their characteristics
        self.models = {
            # Groq Models (Fast inference)
            "groq-llama3-8b": {
                "name": "llama3-8b-8192",
                "provider": "groq",
                "description": "Fast, efficient for quick analysis",
                "strengths": ["Speed", "Reliability"]
            },
            "groq-llama3-70b": {
                "name": "llama3-70b-8192", 
                "provider": "groq",
                "description": "Most capable, detailed insights",
                "strengths": ["Advanced reasoning", "Detailed analysis"]
            },
            "groq-mixtral": {
                "name": "mixtral-8x7b-32768",
                "provider": "groq", 
                "description": "Balanced performance and quality",
                "strengths": ["Multilingual", "Balanced performance"]
            },
            
            # HuggingFace Models (More variety and specialized models)
            "hf-mistral-7b": {
                "name": "mistralai/Mistral-7B-Instruct-v0.2",
                "provider": "huggingface",
                "description": "Powerful 7B model with excellent instruction following",
                "strengths": ["Instruction following", "Efficiency"]
            },
            "hf-phi3-medium": {
                "name": "microsoft/Phi-3-medium-4k-instruct",
                "provider": "huggingface", 
                "description": "Microsoft's efficient reasoning model",
                "strengths": ["Reasoning", "Code understanding"]
            },
            "hf-gemma-7b": {
                "name": "google/gemma-1.1-7b-it",
                "provider": "huggingface",
                "description": "Google's Gemma model optimized for conversations",
                "strengths": ["Conversational", "Safety"]
            },
            "hf-zephyr-7b": {
                "name": "HuggingFaceH4/zephyr-7b-beta",
                "provider": "huggingface",
                "description": "Fine-tuned for helpful, harmless conversations",
                "strengths": ["Helpfulness", "Safety", "Chat optimization"]
            }
        }

    def _record_provider_error(self, provider: str, model: str, reason: str, details: Optional[str] = None) -> None:
        """Store concise provider error diagnostics for operational visibility."""
        self.last_provider_errors[provider] = {
            "model": model,
            "reason": reason,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

    def _provider_for_model(self, model: str) -> str:
        return self.models.get(model, {}).get("provider", "unknown")

    @staticmethod
    def _snippet(text: str, length: int = 240) -> str:
        return text[:length] if text else ""
    
    async def analyze_sentiment(self, text: str, model: str = "groq-llama3-8b") -> dict:
        """Enhanced sentiment analysis with real AI"""
        print(f"🎯 Sentiment Analysis Request - Model: {model}, Text length: {len(text)}")
        
        try:
            if model in self.models:
                print(f"🔍 Model found in registry: {model}")
                if self.models[model]["provider"] == "groq" and self.groq_api_key:
                    print(f"✅ Using Groq API for {model}")
                    return await self._groq_sentiment(text, model)
                elif self.models[model]["provider"] == "huggingface" and self.hf_api_key:
                    print(f"✅ Using HuggingFace API for {model}")
                    return await self._hf_sentiment(text, model)
                else:
                    print(f"⚠️ No valid API key for {model} provider: {self.models[model]['provider']}")
                    print(f"   Groq key present: {bool(self.groq_api_key)}")
                    print(f"   HF key present: {bool(self.hf_api_key)}")
                    provider = self._provider_for_model(model)
                    return self._fallback_sentiment(
                        text,
                        reason=f"missing_api_key_for_{provider}",
                        requested_model=model,
                        provider_requested=provider,
                    )
            else:
                print(f"❌ Model not found in registry: {model}")
                return self._fallback_sentiment(
                    text,
                    reason="unknown_model",
                    requested_model=model,
                    provider_requested="unknown",
                )
        except Exception as e:
            print(f"❌ AI service error in analyze_sentiment: {e}")
            import traceback
            traceback.print_exc()
            provider = self._provider_for_model(model)
            self._record_provider_error(provider, model, "orchestration_exception", str(e))
            return self._fallback_sentiment(
                text,
                reason="orchestration_exception",
                requested_model=model,
                provider_requested=provider,
                error_details=str(e),
            )
    
    async def generate_insights(self, text: str, model: str = "groq-llama3-8b") -> dict:
        """Generate personal insights with real AI"""
        try:
            if model in self.models:
                if self.models[model]["provider"] == "groq" and self.groq_api_key:
                    return await self._groq_insights(text, model)
                elif self.models[model]["provider"] == "huggingface" and self.hf_api_key:
                    return await self._hf_insights(text, model)
                else:
                    provider = self._provider_for_model(model)
                    return self._fallback_insights(
                        text,
                        reason=f"missing_api_key_for_{provider}",
                        requested_model=model,
                        provider_requested=provider,
                    )
            else:
                return self._fallback_insights(
                    text,
                    reason="unknown_model",
                    requested_model=model,
                    provider_requested="unknown",
                )
        except Exception as e:
            provider = self._provider_for_model(model)
            self._record_provider_error(provider, model, "orchestration_exception", str(e))
            return self._fallback_insights(
                text,
                reason="orchestration_exception",
                requested_model=model,
                provider_requested=provider,
                error_details=str(e),
            )
    
    async def summarize_text(self, text: str, model: str = "groq-llama3-8b") -> dict:
        """Summarize journal entry with real AI"""
        try:
            if model in self.models:
                if self.models[model]["provider"] == "groq" and self.groq_api_key:
                    return await self._groq_summarize(text, model)
                elif self.models[model]["provider"] == "huggingface" and self.hf_api_key:
                    return await self._hf_summarize(text, model)
                else:
                    provider = self._provider_for_model(model)
                    return self._fallback_summarize(
                        text,
                        reason=f"missing_api_key_for_{provider}",
                        requested_model=model,
                        provider_requested=provider,
                    )
            else:
                return self._fallback_summarize(
                    text,
                    reason="unknown_model",
                    requested_model=model,
                    provider_requested="unknown",
                )
        except Exception as e:
            provider = self._provider_for_model(model)
            self._record_provider_error(provider, model, "orchestration_exception", str(e))
            return self._fallback_summarize(
                text,
                reason="orchestration_exception",
                requested_model=model,
                provider_requested=provider,
                error_details=str(e),
            )
    
    async def _groq_sentiment(self, text: str, model: str) -> dict:
        """Real Groq-powered sentiment analysis"""
        prompt = f"""Analyze the emotional tone and sentiment of this journal entry with deep psychological insight.

Journal Entry:
"{text}"

Provide a detailed sentiment analysis that includes:
1. Primary emotional state and intensity
2. Underlying emotional patterns or conflicts
3. Emotional triggers or catalysts mentioned
4. Suggestions for emotional wellbeing or reflection

Format your response as a supportive, insightful analysis that helps the person understand their emotional landscape better. Be specific to their actual words and experiences."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.groq_base_url,
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.models[model]["name"],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 300
                    }
                )

                if response.status_code != 200:
                    details = f"status={response.status_code} body={self._snippet(response.text)}"
                    self._record_provider_error("groq", model, "groq_http_error", details)
                    return self._fallback_sentiment(
                        text,
                        reason="groq_http_error",
                        requested_model=model,
                        provider_requested="groq",
                        error_details=details,
                    )
                
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                # Extract sentiment polarity
                sentiment = "neutral"
                if any(word in ai_response.lower() for word in ["positive", "happy", "joy", "excited", "optimistic"]):
                    sentiment = "positive"
                elif any(word in ai_response.lower() for word in ["negative", "sad", "angry", "frustrated", "anxious"]):
                    sentiment = "negative"
                
                return {
                    "result": f"✨ {ai_response}",
                    "confidence": 0.92,
                    "sentiment": sentiment,
                    "model": model,
                    "provider_used": "groq",
                    "provider_requested": "groq",
                    "fallback_used": False,
                    "fallback_reason": None,
                }
                
        except Exception as e:
            print(f"Groq API error: {e}")
            self._record_provider_error("groq", model, "groq_exception", str(e))
            return self._fallback_sentiment(
                text,
                reason="groq_exception",
                requested_model=model,
                provider_requested="groq",
                error_details=str(e),
            )
    
    async def _groq_insights(self, text: str, model: str) -> dict:
        """Real Groq-powered insights"""
        prompt = f"""As an insightful life coach and psychologist, analyze this journal entry to provide personalized insights that will genuinely help this person grow and understand themselves better.

Journal Entry:
"{text}"

Provide specific, actionable insights that:
1. Identify key patterns in their thinking or behavior
2. Highlight strengths and growth opportunities
3. Suggest concrete next steps or reflections
4. Connect their experiences to broader life themes

Be specific to THEIR actual words and situation. Avoid generic advice. Focus on what will be most valuable for their personal development based on what they've shared."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.groq_base_url,
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.models[model]["name"],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.8,
                        "max_tokens": 350
                    }
                )

                if response.status_code != 200:
                    details = f"status={response.status_code} body={self._snippet(response.text)}"
                    self._record_provider_error("groq", model, "groq_http_error", details)
                    return self._fallback_insights(
                        text,
                        reason="groq_http_error",
                        requested_model=model,
                        provider_requested="groq",
                        error_details=details,
                    )
                
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                # Extract themes from response
                themes = []
                common_themes = ["growth", "relationships", "career", "self-care", "goals", "emotions", "challenges", "reflection"]
                for theme in common_themes:
                    if theme in ai_response.lower():
                        themes.append(theme)
                
                return {
                    "result": f"🧠 {ai_response}",
                    "confidence": 0.89,
                    "themes": themes[:3],  # Top 3 themes
                    "model": model,
                    "provider_used": "groq",
                    "provider_requested": "groq",
                    "fallback_used": False,
                    "fallback_reason": None,
                }
                
        except Exception as e:
            print(f"Groq API error: {e}")
            self._record_provider_error("groq", model, "groq_exception", str(e))
            return self._fallback_insights(
                text,
                reason="groq_exception",
                requested_model=model,
                provider_requested="groq",
                error_details=str(e),
            )
    
    async def _groq_summarize(self, text: str, model: str) -> dict:
        """Real Groq-powered summarization"""
        word_count = len(text.split())
        
        prompt = f"""Create a concise but comprehensive summary of this journal entry that captures the essential experiences, emotions, and insights. Make it useful for the person to quickly recall what happened and how they felt.

Journal Entry:
"{text}"

Create a summary that:
1. Captures the main events or experiences
2. Preserves the emotional core
3. Highlights any important realizations or decisions
4. Is about 2-3 sentences but rich in meaningful detail

Focus on what this person would most want to remember about this day/experience."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.groq_base_url,
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.models[model]["name"],
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.6,
                        "max_tokens": 200
                    }
                )

                if response.status_code != 200:
                    details = f"status={response.status_code} body={self._snippet(response.text)}"
                    self._record_provider_error("groq", model, "groq_http_error", details)
                    return self._fallback_summarize(
                        text,
                        reason="groq_http_error",
                        requested_model=model,
                        provider_requested="groq",
                        error_details=details,
                    )
                
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                summary_length = len(ai_response.split())
                
                return {
                    "result": f"📝 {ai_response}",
                    "confidence": 0.88,
                    "original_length": word_count,
                    "summary_length": summary_length,
                    "model": model,
                    "provider_used": "groq",
                    "provider_requested": "groq",
                    "fallback_used": False,
                    "fallback_reason": None,
                }
                
        except Exception as e:
            print(f"Groq API error: {e}")
            self._record_provider_error("groq", model, "groq_exception", str(e))
            return self._fallback_summarize(
                text,
                reason="groq_exception",
                requested_model=model,
                provider_requested="groq",
                error_details=str(e),
            )
    
    # HuggingFace API Methods
    async def _hf_sentiment(self, text: str, model: str) -> dict:
        """HuggingFace-powered sentiment analysis"""
        prompt = f"""Analyze the emotional tone and sentiment of this journal entry with deep psychological insight.

Journal Entry:
"{text}"

Provide a detailed sentiment analysis that includes:
1. Primary emotional state and intensity
2. Underlying emotional patterns or conflicts
3. Emotional triggers or catalysts mentioned
4. Suggestions for emotional wellbeing or reflection

Format your response as a supportive, insightful analysis that helps the person understand their emotional landscape better. Be specific to their actual words and experiences."""

        try:
            print(f"🔍 HF Sentiment Analysis - Model: {model}")
            print(f"🔍 HF API Key present: {bool(self.hf_api_key)}")
            print(f"🔍 Model config: {self.models.get(model, 'Unknown')}")
            print(f"🔍 HF Base URL: {self.hf_base_url}")
            print(f"🔍 Full model URL: {self.hf_base_url}/{self.models[model]['name']}")
            
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{self.hf_base_url}/{self.models[model]['name']}",
                    headers={
                        "Authorization": f"Bearer {self.hf_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 300,
                            "temperature": 0.7,
                            "return_full_text": False
                        }
                    }
                )
                
                print(f"🔍 HF API Response Status: {response.status_code}")
                print(f"🔍 HF API Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"🔍 HF API Raw Response: {result}")
                    
                    # Handle different HF response formats
                    ai_response = ""
                    if isinstance(result, list) and len(result) > 0:
                        ai_response = result[0].get("generated_text", "")
                        print(f"🔍 Extracted from list format: {ai_response[:100]}...")
                    elif isinstance(result, dict):
                        ai_response = result.get("generated_text", "") or result.get("text", "") or str(result)
                        print(f"🔍 Extracted from dict format: {ai_response[:100]}...")
                    else:
                        ai_response = str(result)
                        print(f"🔍 Using string format: {ai_response[:100]}...")
                    
                    if not ai_response or len(ai_response.strip()) < 10:
                        print(f"⚠️ HF API returned empty/short response, using fallback")
                        self._record_provider_error("huggingface", model, "hf_empty_response", "empty_or_short_generated_text")
                        return self._fallback_sentiment(
                            text,
                            reason="hf_empty_response",
                            requested_model=model,
                            provider_requested="huggingface",
                            error_details="empty_or_short_generated_text",
                        )
                    
                    # Extract sentiment polarity
                    sentiment = "neutral"
                    if any(word in ai_response.lower() for word in ["positive", "happy", "joy", "excited", "optimistic"]):
                        sentiment = "positive"
                    elif any(word in ai_response.lower() for word in ["negative", "sad", "angry", "frustrated", "anxious"]):
                        sentiment = "negative"
                    
                    print(f"✅ HF API Success - Model: {model}, Length: {len(ai_response)}")
                    return {
                        "result": f"✨ {ai_response}",
                        "confidence": 0.88,
                        "sentiment": sentiment,
                        "model": model,
                        "provider_used": "huggingface",
                        "provider_requested": "huggingface",
                        "fallback_used": False,
                        "fallback_reason": None,
                    }
                else:
                    error_text = response.text[:500] if response.text else "No error text"
                    print(f"❌ HF API HTTP Error: {response.status_code}")
                    print(f"❌ HF API Error Details: {error_text}")
                    details = f"status={response.status_code} body={self._snippet(error_text)}"
                    self._record_provider_error("huggingface", model, "hf_http_error", details)
                    return self._fallback_sentiment(
                        text,
                        reason="hf_http_error",
                        requested_model=model,
                        provider_requested="huggingface",
                        error_details=details,
                    )
                
        except Exception as e:
            print(f"HuggingFace API error: {e}")
            self._record_provider_error("huggingface", model, "hf_exception", str(e))
            return self._fallback_sentiment(
                text,
                reason="hf_exception",
                requested_model=model,
                provider_requested="huggingface",
                error_details=str(e),
            )
    
    async def _hf_insights(self, text: str, model: str) -> dict:
        """HuggingFace-powered insights"""
        prompt = f"""As an insightful life coach and psychologist, analyze this journal entry to provide personalized insights that will genuinely help this person grow and understand themselves better.

Journal Entry:
"{text}"

Provide specific, actionable insights that:
1. Identify key patterns in their thinking or behavior
2. Highlight strengths and growth opportunities
3. Suggest concrete next steps or reflections
4. Connect their experiences to broader life themes

Be specific to THEIR actual words and situation. Avoid generic advice. Focus on what will be most valuable for their personal development based on what they've shared."""

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{self.hf_base_url}/{self.models[model]['name']}",
                    headers={
                        "Authorization": f"Bearer {self.hf_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 350,
                            "temperature": 0.8,
                            "return_full_text": False
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        ai_response = result[0].get("generated_text", "")
                    else:
                        ai_response = str(result)
                    
                    # Extract themes from response
                    themes = []
                    common_themes = ["growth", "relationships", "career", "self-care", "goals", "emotions", "challenges", "reflection"]
                    for theme in common_themes:
                        if theme in ai_response.lower():
                            themes.append(theme)
                    
                    return {
                        "result": f"🧠 {ai_response}",
                        "confidence": 0.85,
                        "themes": themes[:3],  # Top 3 themes
                        "model": model,
                        "provider_used": "huggingface",
                        "provider_requested": "huggingface",
                        "fallback_used": False,
                        "fallback_reason": None,
                    }
                else:
                    print(f"HF API error: {response.status_code} - {response.text}")
                    details = f"status={response.status_code} body={self._snippet(response.text)}"
                    self._record_provider_error("huggingface", model, "hf_http_error", details)
                    return self._fallback_insights(
                        text,
                        reason="hf_http_error",
                        requested_model=model,
                        provider_requested="huggingface",
                        error_details=details,
                    )
                
        except Exception as e:
            print(f"HuggingFace API error: {e}")
            self._record_provider_error("huggingface", model, "hf_exception", str(e))
            return self._fallback_insights(
                text,
                reason="hf_exception",
                requested_model=model,
                provider_requested="huggingface",
                error_details=str(e),
            )
    
    async def _hf_summarize(self, text: str, model: str) -> dict:
        """HuggingFace-powered summarization"""
        word_count = len(text.split())
        
        prompt = f"""Create a concise but comprehensive summary of this journal entry that captures the essential experiences, emotions, and insights. Make it useful for the person to quickly recall what happened and how they felt.

Journal Entry:
"{text}"

Create a summary that:
1. Captures the main events or experiences
2. Preserves the emotional core
3. Highlights any important realizations or decisions
4. Is about 2-3 sentences but rich in meaningful detail

Focus on what this person would most want to remember about this day/experience."""

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{self.hf_base_url}/{self.models[model]['name']}",
                    headers={
                        "Authorization": f"Bearer {self.hf_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 200,
                            "temperature": 0.6,
                            "return_full_text": False
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        ai_response = result[0].get("generated_text", "")
                    else:
                        ai_response = str(result)
                    
                    summary_length = len(ai_response.split())
                    
                    return {
                        "result": f"📝 {ai_response}",
                        "confidence": 0.82,
                        "original_length": word_count,
                        "summary_length": summary_length,
                        "model": model,
                        "provider_used": "huggingface",
                        "provider_requested": "huggingface",
                        "fallback_used": False,
                        "fallback_reason": None,
                    }
                else:
                    print(f"HF API error: {response.status_code} - {response.text}")
                    details = f"status={response.status_code} body={self._snippet(response.text)}"
                    self._record_provider_error("huggingface", model, "hf_http_error", details)
                    return self._fallback_summarize(
                        text,
                        reason="hf_http_error",
                        requested_model=model,
                        provider_requested="huggingface",
                        error_details=details,
                    )
                
        except Exception as e:
            print(f"HuggingFace API error: {e}")
            self._record_provider_error("huggingface", model, "hf_exception", str(e))
            return self._fallback_summarize(
                text,
                reason="hf_exception",
                requested_model=model,
                provider_requested="huggingface",
                error_details=str(e),
            )
    
    def _fallback_sentiment(
        self,
        text: str,
        reason: str = "fallback_default",
        requested_model: str = "unknown",
        provider_requested: str = "unknown",
        error_details: Optional[str] = None,
    ) -> dict:
        """Intelligent fallback sentiment analysis"""
        self.fallback_count += 1
        positive_words = ["happy", "good", "great", "excellent", "amazing", "wonderful", "love", "excited", "joy"]
        negative_words = ["sad", "bad", "terrible", "awful", "hate", "angry", "frustrated", "disappointed"]
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            confidence = 0.75
        elif neg_count > pos_count:
            sentiment = "negative"
            confidence = 0.75
        else:
            sentiment = "neutral"
            confidence = 0.70
        
        return {
            "result": f"📊 Sentiment: {sentiment.title()} - Your journal entry reflects a {sentiment} emotional tone.",
            "confidence": confidence,
            "sentiment": sentiment,
            "model": "fallback-analysis",
            "provider_used": "fallback",
            "provider_requested": provider_requested,
            "requested_model": requested_model,
            "fallback_used": True,
            "fallback_reason": reason,
            "error_details": self._snippet(error_details or ""),
        }
    
    def _fallback_insights(
        self,
        text: str,
        reason: str = "fallback_default",
        requested_model: str = "unknown",
        provider_requested: str = "unknown",
        error_details: Optional[str] = None,
    ) -> dict:
        """Intelligent fallback insights"""
        self.fallback_count += 1
        insights = [
            "Your writing shows self-awareness and introspection",
            "Consider the emotional patterns in your daily experiences",
            "Notice the balance between challenges and positive moments",
            "Your journal reveals personal growth opportunities"
        ]
        
        import random
        selected_insight = random.choice(insights)
        
        return {
            "result": f"🔍 Insight: {selected_insight}. Continue this reflective practice for deeper self-understanding.",
            "confidence": 0.70,
            "themes": ["self-awareness", "growth", "reflection"],
            "model": "fallback-analysis",
            "provider_used": "fallback",
            "provider_requested": provider_requested,
            "requested_model": requested_model,
            "fallback_used": True,
            "fallback_reason": reason,
            "error_details": self._snippet(error_details or ""),
        }
    
    def _fallback_summarize(
        self,
        text: str,
        reason: str = "fallback_default",
        requested_model: str = "unknown",
        provider_requested: str = "unknown",
        error_details: Optional[str] = None,
    ) -> dict:
        """Intelligent fallback summarization"""
        self.fallback_count += 1
        sentences = text.split('.')
        word_count = len(text.split())
        
        # Simple extractive summary - take first and important sentences
        if len(sentences) > 2:
            summary = f"{sentences[0].strip()}. {sentences[-2].strip() if len(sentences) > 2 else ''}"
        else:
            summary = text[:100] + "..." if len(text) > 100 else text
        
        return {
            "result": f"📄 Summary: {summary.strip()}",
            "confidence": 0.65,
            "original_length": word_count,
            "summary_length": len(summary.split()),
            "model": "fallback-analysis",
            "provider_used": "fallback",
            "provider_requested": provider_requested,
            "requested_model": requested_model,
            "fallback_used": True,
            "fallback_reason": reason,
            "error_details": self._snippet(error_details or ""),
        }

# Initialize enhanced AI service
ai_service = EnhancedAIService()

# Routes
@app.get("/")
async def root():
    return {
        "message": "🚀 AI Journal Summarizer API is running on Railway!",
        "version": "1.0.0",
        "status": "healthy",
        "environment": "production",
        "features": ["sentiment", "insights", "summarize"],
        "groq_connected": bool(os.getenv("GROQ_API_KEY")),
        "hf_connected": bool(os.getenv("HUGGINGFACE_API_KEY"))
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "ai-journal-summarizer-api",
        "platform": "railway",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ai/diagnostics")
async def ai_diagnostics():
    """Operational diagnostics for provider connectivity and fallback behavior."""
    return {
        "status": "ok",
        "groq_configured": bool(ai_service.groq_api_key),
        "hf_configured": bool(ai_service.hf_api_key),
        "fallback_count": ai_service.fallback_count,
        "last_provider_errors": ai_service.last_provider_errors,
        "timestamp": datetime.now().isoformat(),
    }

@app.post("/api/ai/sentiment", response_model=TextProcessResponse)
async def analyze_sentiment(request: TextProcessRequest):
    """Analyze sentiment of journal entry with model selection"""
    try:
        result_data = await ai_service.analyze_sentiment(request.text, request.model)
        
        return TextProcessResponse(
            result=result_data["result"],
            task_type="sentiment",
            confidence=result_data["confidence"],
            metadata={
                "word_count": len(request.text.split()),
                "sentiment": result_data.get("sentiment", "unknown"),
                "model": result_data.get("model", request.model),
                "requested_model": result_data.get("requested_model", request.model),
                "provider_used": result_data.get("provider_used", "unknown"),
                "provider_requested": result_data.get("provider_requested", ai_service._provider_for_model(request.model)),
                "fallback_used": result_data.get("fallback_used", result_data.get("model") == "fallback-analysis"),
                "fallback_reason": result_data.get("fallback_reason"),
                "error_details": result_data.get("error_details"),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@app.post("/api/ai/insights", response_model=TextProcessResponse)
async def generate_insights(request: TextProcessRequest):
    """Generate personal insights from journal entry with model selection"""
    try:
        result_data = await ai_service.generate_insights(request.text, request.model)
        
        return TextProcessResponse(
            result=result_data["result"],
            task_type="insights",
            confidence=result_data["confidence"],
            metadata={
                "word_count": len(request.text.split()),
                "themes": result_data.get("themes", []),
                "model": result_data.get("model", request.model),
                "requested_model": result_data.get("requested_model", request.model),
                "provider_used": result_data.get("provider_used", "unknown"),
                "provider_requested": result_data.get("provider_requested", ai_service._provider_for_model(request.model)),
                "fallback_used": result_data.get("fallback_used", result_data.get("model") == "fallback-analysis"),
                "fallback_reason": result_data.get("fallback_reason"),
                "error_details": result_data.get("error_details"),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@app.post("/api/ai/summarize", response_model=TextProcessResponse)
async def summarize_text(request: TextProcessRequest):
    """Summarize journal entry with model selection"""
    try:
        result_data = await ai_service.summarize_text(request.text, request.model)
        
        return TextProcessResponse(
            result=result_data["result"],
            task_type="summarize",
            confidence=result_data["confidence"],
            metadata={
                "original_length": result_data.get("original_length", 0),
                "summary_length": result_data.get("summary_length", 0),
                "model": result_data.get("model", request.model),
                "requested_model": result_data.get("requested_model", request.model),
                "provider_used": result_data.get("provider_used", "unknown"),
                "provider_requested": result_data.get("provider_requested", ai_service._provider_for_model(request.model)),
                "fallback_used": result_data.get("fallback_used", result_data.get("model") == "fallback-analysis"),
                "fallback_reason": result_data.get("fallback_reason"),
                "error_details": result_data.get("error_details"),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

# Add new endpoint to get available models
@app.get("/api/ai/models")
async def get_available_models():
    """Get list of available AI models"""
    return {
        "models": ai_service.models,
        "default": "groq-llama3-8b",
        "groq_connected": bool(ai_service.groq_api_key),
        "hf_connected": bool(ai_service.hf_api_key)
    }

# Railway entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
