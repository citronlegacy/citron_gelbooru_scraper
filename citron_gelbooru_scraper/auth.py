"""
Authentication module for Gelbooru API.

Handles API key and user ID validation and authentication.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class GelbooruAuth(BaseModel):
    """Gelbooru API authentication credentials."""
    
    api_key: str = Field(..., min_length=1, description="Gelbooru API key")
    user_id: str = Field(..., min_length=1, description="Gelbooru user ID")
    
    @field_validator("api_key", "user_id")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure credentials are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Credentials cannot be empty")
        return v.strip()
    
    def get_auth_params(self) -> dict[str, str]:
        """
        Get authentication parameters for API requests.
        
        Returns:
            dict: Authentication parameters with api_key and user_id
        """
        return {
            "api_key": self.api_key,
            "user_id": self.user_id
        }


def validate_credentials(api_key: str, user_id: str) -> GelbooruAuth:
    """
    Validate and create authentication object.
    
    Args:
        api_key: Gelbooru API key
        user_id: Gelbooru user ID
        
    Returns:
        GelbooruAuth: Validated authentication object
        
    Raises:
        ValueError: If credentials are invalid
    """
    try:
        return GelbooruAuth(api_key=api_key, user_id=user_id)
    except Exception as e:
        raise ValueError(f"Invalid credentials: {e}")
