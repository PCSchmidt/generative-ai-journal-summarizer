from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ...services.ai_service_simple import ai_service
from ...services.vector_store_simple import vector_store_service
from ..dependencies_simple import get_current_user

router = APIRouter()

class TextProcessRequest(BaseModel):
    text: str
    task_type: str = "analyze"

class TextProcessResponse(BaseModel):
    result: str
    task_type: str
    confidence: float
    metadata: dict

class SearchRequest(BaseModel):
    query: str
    k: int = 5

@router.post("/process", response_model=TextProcessResponse)
async def process_text(
    request: TextProcessRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process text with AI"""
    try:
        result = await ai_service.process_text(request.text, request.task_type)
        return TextProcessResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/search")
async def search_similar(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Search for similar content"""
    try:
        results = await vector_store_service.search(request.query, request.k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/add-knowledge")
async def add_knowledge(
    texts: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Add texts to knowledge base"""
    try:
        await vector_store_service.add_documents(texts)
        return {"message": f"Added {len(texts)} documents to knowledge base"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add knowledge: {str(e)}")
