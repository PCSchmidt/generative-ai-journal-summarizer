from typing import Dict

async def get_current_user() -> Dict:
    """Simplified auth - returns a mock user for development"""
    return {
        "id": "dev-user-001",
        "username": "developer",
        "email": "dev@example.com"
    }
