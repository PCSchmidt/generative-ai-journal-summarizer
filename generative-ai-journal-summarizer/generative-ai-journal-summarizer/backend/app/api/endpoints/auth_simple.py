from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    """Simple login endpoint"""
    return {
        "access_token": "dev-token-123",
        "token_type": "bearer",
        "user": {
            "id": "dev-user-001",
            "username": "developer",
            "email": "dev@example.com"
        }
    }

@router.post("/register")
async def register():
    """Simple register endpoint"""
    return {
        "message": "User registered successfully",
        "user": {
            "id": "dev-user-001",
            "username": "developer",
            "email": "dev@example.com"
        }
    }
