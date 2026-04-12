# Railway Production FastAPI Backend - AI Journal Summarizer
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
import json
import base64
import hashlib
import uuid
from datetime import datetime
import httpx
import random
from typing import Optional, List, Dict, Any
from cryptography.fernet import Fernet

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
    user_token_id: Optional[str] = None

class TextProcessResponse(BaseModel):
    result: str
    task_type: str
    confidence: float
    metadata: dict

class ConnectTokenRequest(BaseModel):
    provider: str
    token: str
    label: Optional[str] = None

# Enhanced AI Service with Real Groq Integration
class EnhancedAIService:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.together_api_key = os.getenv("TOGETHER_API_KEY")
        self.groq_base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.hf_base_url = "https://api-inference.huggingface.co/models"
        self.fallback_count = 0
        self.last_provider_errors: Dict[str, Dict[str, Any]] = {}

        secret_seed = os.getenv("TOKEN_ENCRYPTION_KEY") or os.getenv("SECRET_KEY") or "ai-journal-local-dev-seed"
        derived_key = base64.urlsafe_b64encode(hashlib.sha256(secret_seed.encode("utf-8")).digest())
        self.fernet = Fernet(derived_key)
        self.user_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Debug: Log API key status
        print(f"🔑 API Keys Status:")
        print(f"   GROQ_API_KEY: {'✅ Present' if self.groq_api_key else '❌ Missing'}")
        print(f"   HUGGINGFACE_API_KEY: {'✅ Present' if self.hf_api_key else '❌ Missing'}")
        print(f"   OPENAI_API_KEY: {'✅ Present' if self.openai_api_key else '❌ Missing'}")
        print(f"   ANTHROPIC_API_KEY: {'✅ Present' if self.anthropic_api_key else '❌ Missing'}")
        print(f"   GOOGLE_API_KEY: {'✅ Present' if self.google_api_key else '❌ Missing'}")
        print(f"   MISTRAL_API_KEY: {'✅ Present' if self.mistral_api_key else '❌ Missing'}")
        print(f"   OPENROUTER_API_KEY: {'✅ Present' if self.openrouter_api_key else '❌ Missing'}")
        print(f"   TOGETHER_API_KEY: {'✅ Present' if self.together_api_key else '❌ Missing'}")
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
                "strengths": ["Helpfulness", "Safety", "Chat optimization"],
                "tier": "free"
            },

            # Premium / BYOK capable models
            "premium-openai-gpt-4.1": {
                "name": "gpt-4.1",
                "provider": "openai",
                "description": "Top-tier multimodal reasoning model",
                "strengths": ["Reasoning", "Reliability", "Enterprise quality"],
                "tier": "premium"
            },
            "premium-openai-o3": {
                "name": "o3",
                "provider": "openai",
                "description": "High-end reasoning model for complex tasks",
                "strengths": ["Advanced planning", "Problem solving"],
                "tier": "premium"
            },
            "premium-anthropic-claude-3.7": {
                "name": "claude-3-7-sonnet-latest",
                "provider": "anthropic",
                "description": "Anthropic flagship balanced model",
                "strengths": ["Safety", "Nuance", "Long-form quality"],
                "tier": "premium"
            },
            "premium-google-gemini-2.5": {
                "name": "gemini-2.5-pro",
                "provider": "google",
                "description": "Gemini high-end model for deep analysis",
                "strengths": ["Reasoning", "Context handling"],
                "tier": "premium"
            },
            "premium-mistral-large": {
                "name": "mistral-large-latest",
                "provider": "mistral",
                "description": "Mistral premium flagship model",
                "strengths": ["Multilingual quality", "Precision"],
                "tier": "premium"
            },
            "premium-openrouter-claude-3.7": {
                "name": "anthropic/claude-3.7-sonnet",
                "provider": "openrouter",
                "description": "Claude 3.7 Sonnet through OpenRouter",
                "strengths": ["Reasoning", "Writing quality", "Provider portability"],
                "tier": "premium"
            },
            "premium-openrouter-gemini-2.5": {
                "name": "google/gemini-2.5-pro-preview",
                "provider": "openrouter",
                "description": "Gemini 2.5 Pro through OpenRouter",
                "strengths": ["Long-context reasoning", "Provider portability"],
                "tier": "premium"
            },
            "premium-openrouter-deepseek-r1": {
                "name": "deepseek/deepseek-r1",
                "provider": "openrouter",
                "description": "DeepSeek R1 through OpenRouter",
                "strengths": ["Math and logic", "Cost-performance"],
                "tier": "premium"
            },
            "premium-together-llama-3.1-405b": {
                "name": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                "provider": "together",
                "description": "Llama 3.1 405B via Together AI",
                "strengths": ["Large-model reasoning", "Cost control"],
                "tier": "premium"
            },
            "premium-together-mixtral-8x22b": {
                "name": "mistralai/Mixtral-8x22B-Instruct-v0.1",
                "provider": "together",
                "description": "Mixtral 8x22B via Together AI",
                "strengths": ["Quality-speed balance", "Strong instruction following"],
                "tier": "premium"
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

    def connect_user_token(self, provider: str, token: str, label: Optional[str] = None) -> Dict[str, Any]:
        """Encrypt and store a BYOK token in memory for this runtime."""
        token_id = str(uuid.uuid4())
        encrypted = self.fernet.encrypt(token.encode("utf-8")).decode("utf-8")
        self.user_tokens[token_id] = {
            "provider": provider,
            "encrypted_token": encrypted,
            "label": label or "",
            "created_at": datetime.now().isoformat(),
            "last4": token[-4:] if len(token) >= 4 else "****",
        }
        return {
            "token_id": token_id,
            "provider": provider,
            "label": label or "",
            "last4": self.user_tokens[token_id]["last4"],
            "created_at": self.user_tokens[token_id]["created_at"],
        }

    def _get_user_token_for_provider(self, provider: str, token_id: Optional[str]) -> Optional[str]:
        if not token_id:
            return None
        token_data = self.user_tokens.get(token_id)
        if not token_data or token_data.get("provider") != provider:
            return None
        encrypted = token_data.get("encrypted_token", "")
        if not encrypted:
            return None
        try:
            return self.fernet.decrypt(encrypted.encode("utf-8")).decode("utf-8")
        except Exception:
            return None

    def _server_provider_key(self, provider: str) -> Optional[str]:
        return {
            "groq": self.groq_api_key,
            "huggingface": self.hf_api_key,
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "mistral": self.mistral_api_key,
            "openrouter": self.openrouter_api_key,
            "together": self.together_api_key,
        }.get(provider)

    def _resolve_provider_auth(self, provider: str, user_token_id: Optional[str]) -> Dict[str, Any]:
        """Resolve auth source (BYOK first, then server key)."""
        byok = self._get_user_token_for_provider(provider, user_token_id)
        if byok:
            return {"ok": True, "token": byok, "auth_source": "user_token"}

        server_key = self._server_provider_key(provider)
        if server_key:
            return {"ok": True, "token": server_key, "auth_source": "server_key"}

        return {"ok": False, "token": None, "auth_source": "none"}

    def _model_availability(self, model_key: str) -> Dict[str, Any]:
        model = self.models.get(model_key, {})
        provider = model.get("provider", "unknown")
        tier = model.get("tier", "free")
        server_key = bool(self._server_provider_key(provider))
        user_token_count = sum(1 for t in self.user_tokens.values() if t.get("provider") == provider)
        available = tier == "free" or server_key or user_token_count > 0
        reason = "available" if available else "requires_plan_or_byok"
        return {
            "tier": tier,
            "provider": provider,
            "available": available,
            "availability_reason": reason,
            "server_key_configured": server_key,
            "user_token_connected": user_token_count > 0,
        }

    async def _call_openai_compatible(
        self,
        provider: str,
        base_url: str,
        model_name: str,
        prompt: str,
        token: str,
        max_tokens: int,
        temperature: float,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> str:
        async with httpx.AsyncClient(timeout=35.0) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            if extra_headers:
                headers.update(extra_headers)

            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            if response.status_code != 200:
                details = f"status={response.status_code} body={self._snippet(response.text)}"
                self._record_provider_error(provider, model_name, f"{provider}_http_error", details)
                raise RuntimeError(details)

            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_anthropic(self, model_name: str, prompt: str, token: str, max_tokens: int, temperature: float) -> str:
        async with httpx.AsyncClient(timeout=35.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": token,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model_name,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            if response.status_code != 200:
                details = f"status={response.status_code} body={self._snippet(response.text)}"
                self._record_provider_error("anthropic", model_name, "anthropic_http_error", details)
                raise RuntimeError(details)

            data = response.json()
            content = data.get("content", [])
            if not content:
                raise RuntimeError("anthropic_empty_response")
            return content[0].get("text", "")

    async def _call_google_gemini(self, model_name: str, prompt: str, token: str, max_tokens: int, temperature: float) -> str:
        async with httpx.AsyncClient(timeout=35.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={token}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    },
                },
            )
            if response.status_code != 200:
                details = f"status={response.status_code} body={self._snippet(response.text)}"
                self._record_provider_error("google", model_name, "google_http_error", details)
                raise RuntimeError(details)

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError("google_empty_response")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise RuntimeError("google_empty_parts")
            return parts[0].get("text", "")

    async def _premium_chat(self, model_key: str, prompt: str, max_tokens: int, temperature: float, user_token_id: Optional[str]) -> Dict[str, Any]:
        model_cfg = self.models.get(model_key, {})
        provider = model_cfg.get("provider", "unknown")
        model_name = model_cfg.get("name", model_key)
        auth = self._resolve_provider_auth(provider, user_token_id)

        if not auth["ok"]:
            return {
                "ok": False,
                "reason": "premium_auth_required",
                "provider": provider,
                "model": model_key,
                "error": "No server key or BYOK token configured for provider",
            }

        token = auth["token"]
        auth_source = auth["auth_source"]

        try:
            if provider == "openai":
                content = await self._call_openai_compatible(provider, "https://api.openai.com/v1", model_name, prompt, token, max_tokens, temperature)
            elif provider == "openrouter":
                content = await self._call_openai_compatible(
                    provider,
                    "https://openrouter.ai/api/v1",
                    model_name,
                    prompt,
                    token,
                    max_tokens,
                    temperature,
                    extra_headers={
                        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "https://github.com/PCSchmidt/generative-ai-journal-summarizer"),
                        "X-Title": os.getenv("OPENROUTER_APP_NAME", "AI Journal Intelligence"),
                    },
                )
            elif provider == "together":
                content = await self._call_openai_compatible(
                    provider,
                    "https://api.together.xyz/v1",
                    model_name,
                    prompt,
                    token,
                    max_tokens,
                    temperature,
                )
            elif provider == "mistral":
                content = await self._call_openai_compatible(provider, "https://api.mistral.ai/v1", model_name, prompt, token, max_tokens, temperature)
            elif provider == "anthropic":
                content = await self._call_anthropic(model_name, prompt, token, max_tokens, temperature)
            elif provider == "google":
                content = await self._call_google_gemini(model_name, prompt, token, max_tokens, temperature)
            else:
                return {
                    "ok": False,
                    "reason": "provider_not_supported",
                    "provider": provider,
                    "model": model_key,
                    "error": f"Provider '{provider}' is not implemented",
                }

            return {
                "ok": True,
                "content": content,
                "provider": provider,
                "model": model_key,
                "auth_source": auth_source,
            }
        except Exception as e:
            self._record_provider_error(provider, model_key, "premium_provider_exception", str(e))
            return {
                "ok": False,
                "reason": "premium_provider_exception",
                "provider": provider,
                "model": model_key,
                "error": str(e),
            }
    
    async def analyze_sentiment(self, text: str, model: str = "groq-llama3-8b", user_token_id: Optional[str] = None) -> dict:
        """Enhanced sentiment analysis with real AI"""
        print(f"🎯 Sentiment Analysis Request - Model: {model}, Text length: {len(text)}")
        
        try:
            if model in self.models:
                model_tier = self.models[model].get("tier", "free")
                if model_tier == "premium":
                    prompt = f"Analyze the emotional tone and sentiment of this journal entry with deep psychological insight. Journal Entry: \"{text}\""
                    premium = await self._premium_chat(model, prompt, max_tokens=300, temperature=0.7, user_token_id=user_token_id)
                    if premium.get("ok"):
                        ai_response = premium.get("content", "")
                        sentiment = "neutral"
                        if any(word in ai_response.lower() for word in ["positive", "happy", "joy", "excited", "optimistic"]):
                            sentiment = "positive"
                        elif any(word in ai_response.lower() for word in ["negative", "sad", "angry", "frustrated", "anxious"]):
                            sentiment = "negative"
                        return {
                            "result": f"✨ {ai_response}",
                            "confidence": 0.93,
                            "sentiment": sentiment,
                            "model": model,
                            "provider_used": premium.get("provider"),
                            "provider_requested": premium.get("provider"),
                            "fallback_used": False,
                            "fallback_reason": None,
                            "auth_source": premium.get("auth_source"),
                        }
                    return self._fallback_sentiment(
                        text,
                        reason=premium.get("reason", "premium_error"),
                        requested_model=model,
                        provider_requested=self._provider_for_model(model),
                        error_details=premium.get("error"),
                    )

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
    
    async def generate_insights(self, text: str, model: str = "groq-llama3-8b", user_token_id: Optional[str] = None) -> dict:
        """Generate personal insights with real AI"""
        try:
            if model in self.models:
                model_tier = self.models[model].get("tier", "free")
                if model_tier == "premium":
                    prompt = f"As an insightful life coach and psychologist, analyze this journal entry for actionable insights: \"{text}\""
                    premium = await self._premium_chat(model, prompt, max_tokens=350, temperature=0.8, user_token_id=user_token_id)
                    if premium.get("ok"):
                        ai_response = premium.get("content", "")
                        themes = []
                        common_themes = ["growth", "relationships", "career", "self-care", "goals", "emotions", "challenges", "reflection"]
                        for theme in common_themes:
                            if theme in ai_response.lower():
                                themes.append(theme)
                        return {
                            "result": f"🧠 {ai_response}",
                            "confidence": 0.91,
                            "themes": themes[:3],
                            "model": model,
                            "provider_used": premium.get("provider"),
                            "provider_requested": premium.get("provider"),
                            "fallback_used": False,
                            "fallback_reason": None,
                            "auth_source": premium.get("auth_source"),
                        }
                    return self._fallback_insights(
                        text,
                        reason=premium.get("reason", "premium_error"),
                        requested_model=model,
                        provider_requested=self._provider_for_model(model),
                        error_details=premium.get("error"),
                    )

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
    
    async def summarize_text(self, text: str, model: str = "groq-llama3-8b", user_token_id: Optional[str] = None) -> dict:
        """Summarize journal entry with real AI"""
        try:
            if model in self.models:
                model_tier = self.models[model].get("tier", "free")
                if model_tier == "premium":
                    prompt = f"Create a concise but comprehensive summary of this journal entry: \"{text}\""
                    premium = await self._premium_chat(model, prompt, max_tokens=200, temperature=0.6, user_token_id=user_token_id)
                    if premium.get("ok"):
                        ai_response = premium.get("content", "")
                        return {
                            "result": f"📝 {ai_response}",
                            "confidence": 0.9,
                            "original_length": len(text.split()),
                            "summary_length": len(ai_response.split()),
                            "model": model,
                            "provider_used": premium.get("provider"),
                            "provider_requested": premium.get("provider"),
                            "fallback_used": False,
                            "fallback_reason": None,
                            "auth_source": premium.get("auth_source"),
                        }
                    return self._fallback_summarize(
                        text,
                        reason=premium.get("reason", "premium_error"),
                        requested_model=model,
                        provider_requested=self._provider_for_model(model),
                        error_details=premium.get("error"),
                    )

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
        "connected_tokens": len(ai_service.user_tokens),
        "fallback_count": ai_service.fallback_count,
        "last_provider_errors": ai_service.last_provider_errors,
        "timestamp": datetime.now().isoformat(),
    }

@app.post("/api/ai/sentiment", response_model=TextProcessResponse)
async def analyze_sentiment(request: TextProcessRequest):
    """Analyze sentiment of journal entry with model selection"""
    try:
        result_data = await ai_service.analyze_sentiment(request.text, request.model, request.user_token_id)
        
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
                "auth_source": result_data.get("auth_source", "server_key"),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@app.post("/api/ai/insights", response_model=TextProcessResponse)
async def generate_insights(request: TextProcessRequest):
    """Generate personal insights from journal entry with model selection"""
    try:
        result_data = await ai_service.generate_insights(request.text, request.model, request.user_token_id)
        
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
                "auth_source": result_data.get("auth_source", "server_key"),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@app.post("/api/ai/summarize", response_model=TextProcessResponse)
async def summarize_text(request: TextProcessRequest):
    """Summarize journal entry with model selection"""
    try:
        result_data = await ai_service.summarize_text(request.text, request.model, request.user_token_id)
        
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
                "auth_source": result_data.get("auth_source", "server_key"),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

# Add new endpoint to get available models
@app.get("/api/ai/models")
async def get_available_models():
    """Get list of available AI models"""
    availability = {key: ai_service._model_availability(key) for key in ai_service.models.keys()}
    return {
        "models": ai_service.models,
        "availability": availability,
        "default": "groq-llama3-8b",
        "groq_connected": bool(ai_service.groq_api_key),
        "hf_connected": bool(ai_service.hf_api_key)
    }

@app.get("/api/ai/tier-info")
async def get_tier_info():
    """Return model availability for free/premium gating in frontend."""
    models = []
    for key, config in ai_service.models.items():
        availability = ai_service._model_availability(key)
        models.append({
            "key": key,
            "name": config.get("name"),
            "provider": config.get("provider"),
            "tier": config.get("tier", "free"),
            "description": config.get("description", ""),
            "available": availability["available"],
            "availability_reason": availability["availability_reason"],
            "server_key_configured": availability["server_key_configured"],
            "user_token_connected": availability["user_token_connected"],
        })
    return {
        "status": "ok",
        "models": models,
        "timestamp": datetime.now().isoformat(),
    }

@app.post("/api/auth/connect-token")
async def connect_token(request: ConnectTokenRequest):
    """Connect a user-provided provider token (BYOK), stored encrypted in-memory."""
    provider = request.provider.strip().lower()
    if provider not in {"openai", "anthropic", "google", "mistral", "groq", "huggingface", "openrouter", "together"}:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    if not request.token or len(request.token.strip()) < 10:
        raise HTTPException(status_code=400, detail="Token appears invalid")

    token_record = ai_service.connect_user_token(provider, request.token.strip(), request.label)
    return {
        "status": "connected",
        "token": token_record,
        "message": "Token connected and encrypted in runtime vault",
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
