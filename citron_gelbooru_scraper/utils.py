"""
Utility functions for the scraper.

Includes rate limiting, error handling, and helper functions.
"""

import time
import logging
from typing import Optional, Any
from functools import wraps
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class AuthenticationError(ScraperError):
    """Raised when authentication fails."""
    pass


class DownloadError(ScraperError):
    """Raised when download fails."""
    pass


class RateLimitError(ScraperError):
    """Raised when rate limit is exceeded."""
    pass


def rate_limit(min_interval: float = 0.1):
    """
    Decorator to enforce minimum time between function calls.
    
    Args:
        min_interval: Minimum seconds between calls
    """
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        
        return wrapper
    return decorator


def ensure_dir_exists(path: str | Path) -> Path:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def sanitize_filename(filename: str) -> str:
    """
    Remove or replace invalid filename characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Replace invalid characters with underscore
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    return filename


def format_url(base_url: str, params: dict[str, Any]) -> str:
    """
    Format URL with query parameters.
    
    Args:
        base_url: Base URL without parameters
        params: Dictionary of query parameters
        
    Returns:
        Formatted URL string
    """
    # URL encode special characters in params
    encoded_params = []
    for key, value in params.items():
        if value is not None:
            encoded_value = str(value).replace(" ", "+")\
                                       .replace("(", "%28")\
                                       .replace(")", "%29")\
                                       .replace(":", "%3a")\
                                       .replace("&", "%26")
            encoded_params.append(f"{key}={encoded_value}")
    
    query_string = "&".join(encoded_params)
    return f"{base_url}?{query_string}" if query_string else base_url


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
        
        return wrapper
    return decorator


def get_file_extension(url: str) -> str:
    """
    Extract file extension from URL.
    
    Args:
        url: Image URL
        
    Returns:
        File extension including dot (e.g., '.jpg')
    """
    supported_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
    
    url_lower = url.lower()
    for ext in supported_extensions:
        if ext in url_lower:
            return ext
    
    # Default to .jpg if no recognized extension
    return '.jpg'
