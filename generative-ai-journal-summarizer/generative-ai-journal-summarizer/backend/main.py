from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from dotenv import load_dotenv
from app.api.endpoints import auth_simple, ai_enhanced

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Journal Summarizer API",
    version="1.0.0",
    description="AI-powered mobile app backend"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_simple.router, prefix="/api/auth", tags=["authentication"])
app.include_router(ai_enhanced.router, prefix="/api/ai", tags=["ai"])

security = HTTPBearer()

@app.get("/")
async def root():
    return {
        "message": "AI Journal Summarizer API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-journal-summarizer-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True  # Enable reload for development
    )
