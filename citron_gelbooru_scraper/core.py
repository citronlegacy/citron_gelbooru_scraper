"""
Core module for Gelbooru scraper.

Main entrypoint and orchestration logic.
"""

import time
from pathlib import Path
from typing import Optional, Dict, Any

from citron_gelbooru_scraper.auth import validate_credentials, GelbooruAuth
from citron_gelbooru_scraper.downloader import ImageDownloader
from citron_gelbooru_scraper.tags import get_default_blacklist
from citron_gelbooru_scraper.utils import (
    logger,
    ensure_dir_exists,
    format_url,
    ScraperError,
    AuthenticationError
)
from citron_gelbooru_scraper.utils import SAFE_SOLO_QUERY, SORT_SCORE_QUERY

GELBOORU_API_BASE = "https://gelbooru.com/index.php"
DEFAULT_LIMIT = 100  # Hardcoded by Gelbooru API


def build_query_params(
    tags: str,
    api_key: str,
    user_id: str,
    limit: int = DEFAULT_LIMIT,
    page: int = 0
) -> Dict[str, Any]:
    """
    Build query parameters for Gelbooru API request.
    
    Args:
        tags: Search tags (space-separated)
        api_key: Gelbooru API key
        user_id: Gelbooru user ID
        limit: Number of results per page
        page: Page number (0-indexed)
        
    Returns:
        Dictionary of query parameters
    """
    params = {
        "page": "dapi",
        "s": "post",
        "q": "index",
        "json": "1",
        "api_key": api_key,
        "user_id": user_id,
        "tags": tags,
        "limit": str(limit)
    }
    
    if page > 0:
        params["pid"] = str(page)
    
    return params


def jelly_download(
    query: str,
    api_key: str,
    user_id: str,
    output_dir: str,
    max_images: int = 100,
    exclude_tags: Optional[set] = None
) -> Dict[str, Any]:
    """
    Main function to search and download images from Gelbooru.
    
    This is the primary entrypoint for the library. It authenticates with
    Gelbooru, searches for images matching the query, and downloads both
    the images and their associated tags.
    
    Args:
        query: Gelbooru search query (tags separated by spaces)
               Example: "catgirl rating:safe"
        api_key: Your Gelbooru API key
        user_id: Your Gelbooru user ID
        output_dir: Directory to save images and tags
        max_images: Maximum number of images to download (default: 100)
        exclude_tags: Optional set of tags to exclude (uses default blacklist if None)
        
    Returns:
        Dictionary with summary:
        {
            "query": str,
            "total_found": int,
            "downloaded": int,
            "failed": int,
            "output_dir": str,
            "errors": List[str]
        }
        
    Raises:
        AuthenticationError: If credentials are invalid
        ScraperError: If download process fails
        
    Example:
        >>> from gelbooru_scraper.core import jelly_download
        >>> result = jelly_download(
        ...     query="shantae_(series) rating:general",
        ...     api_key="YOUR_API_KEY",
        ...     user_id="YOUR_USER_ID",
        ...     output_dir="./downloads",
        ...     max_images=50
        ... )
        >>> print(f"Downloaded {result['downloaded']} images")
    """
    # Validate credentials
    try:
        auth = validate_credentials(api_key, user_id)
        logger.info("Authentication validated")
    except Exception as e:
        raise AuthenticationError(f"Invalid credentials: {e}")
    
    # Ensure output directory exists
    output_path = ensure_dir_exists(output_dir)
    logger.info(f"Output directory: {output_path}")
    
    # Initialize downloader
    blacklist = exclude_tags or get_default_blacklist()
    downloader = ImageDownloader(output_dir, blacklist)
    
    # Prepare query
    formatted_tags = query.strip()
    logger.info(f"Search query: {formatted_tags}")
    
    # Initial request to get total count
    params = build_query_params(formatted_tags, api_key, user_id, limit=min(max_images, DEFAULT_LIMIT))
    url = format_url(GELBOORU_API_BASE, params)
    
    try:
        data = downloader.get_json(url)
    except Exception as e:
        raise ScraperError(f"Failed to fetch search results: {e}")
    
    # Check if we got results
    attributes = data.get("@attributes", {})
    total_found = int(attributes.get("count", 0))
    
    if total_found == 0:
        logger.warning("No results found for query")
        return {
            "query": query,
            "total_found": 0,
            "downloaded": 0,
            "failed": 0,
            "output_dir": str(output_path),
            "errors": []
        }
    
    logger.info(f"Found {total_found} results")
    
    # Process and download images
    all_posts = data.get("post", [])
    total_downloaded = 0
    total_failed = 0
    all_errors = []
    
    # Calculate how many pages we need
    pages_needed = (max_images + DEFAULT_LIMIT - 1) // DEFAULT_LIMIT
    
    # Process first page
    processed = downloader.process_posts(all_posts[:max_images])
    result = downloader.download_batch(processed)
    total_downloaded += result["downloaded"]
    total_failed += result["failed"]
    all_errors.extend(result["errors"])
    
    # Fetch and process additional pages if needed
    for page in range(1, pages_needed):
        if total_downloaded >= max_images:
            break
        
        # Calculate how many more we need
        remaining = max_images - total_downloaded
        if remaining <= 0:
            break
        
        # Rate limiting between pages
        time.sleep(0.1)
        
        # Fetch next page
        page_limit = min(remaining, DEFAULT_LIMIT)
        params = build_query_params(formatted_tags, api_key, user_id, limit=page_limit, page=page)
        url = format_url(GELBOORU_API_BASE, params)
        
        try:
            page_data = downloader.get_json(url)
            page_posts = page_data.get("post", [])
            
            if not page_posts:
                logger.info("No more results available")
                break
            
            # Process only what we need
            posts_to_process = page_posts[:remaining]
            processed = downloader.process_posts(posts_to_process)
            result = downloader.download_batch(processed)
            
            total_downloaded += result["downloaded"]
            total_failed += result["failed"]
            all_errors.extend(result["errors"])
            
            logger.info(f"Page {page + 1}: Downloaded {result['downloaded']}, Failed {result['failed']}")
            
        except Exception as e:
            logger.error(f"Error processing page {page + 1}: {e}")
            all_errors.append(f"Page {page + 1} error: {e}")
    
    # Summary
    summary = {
        "query": query,
        "total_found": total_found,
        "downloaded": total_downloaded,
        "failed": total_failed,
        "output_dir": str(output_path),
        "errors": all_errors
    }
    
    logger.info(
        f"Download complete: {total_downloaded} successful, "
        f"{total_failed} failed out of {max_images} requested"
    )
    
    return summary


def get_character_tags(
    character_name: str,
    api_key: str,
    user_id: str,
    max_images: int = 100
) -> Dict[str, Any]:
    """
    Extracts character tags (eye, hair, other) from Gelbooru for a given character.
    """
    purge_tags = set([
        "open_mouth", "blush", "closed_mouth", "full_body", "cowboy_shot", "holding", "sitting", "upper_body",
        "simple_background", "looking_at_viewer", "black_background", "smile", "closed_eyes", "standing", "artist_name", "absurdres", "white_background"
    ])
    special_hair_tags = set(["ponytail", "twintails", "braid", "ahoge", "two side up"])

    # Search for character images

    query = f"{character_name} {SAFE_SOLO_QUERY} {SORT_SCORE_QUERY}"
    params = build_query_params(query, api_key, user_id, limit=min(max_images, DEFAULT_LIMIT))
    url = format_url(GELBOORU_API_BASE, params)
    print(f"Fetching character tags with URL: {url}")
    try:
        data = ImageDownloader(".").get_json(url)
    except Exception as e:
        raise ScraperError(f"Failed to fetch character tags: {e}")

    posts = data.get("post", [])
    all_tags = []
    for post in posts[:max_images]:
        tag_str = post.get("tags", "")
        tags = tag_str.split()
        all_tags.extend(tags)

    # Remove purge tags
    filtered_tags = [t for t in all_tags if t.lower() not in purge_tags]
    # Only consider the top 50 tags
    from citron_gelbooru_scraper.utils import get_top_tags
    top_tags = get_top_tags(filtered_tags, top_n=50)

    top_tags = [t.replace("_", " ") for t in top_tags]
    eye_tags = [t for t in top_tags if "eye" in t.lower() or "eyes" in t.lower()]
    hair_tags = [t for t in top_tags if "hair" in t.lower() or t.lower() in special_hair_tags]
    other_tags = [t for t in top_tags if t not in eye_tags and t not in hair_tags]

    character_tags = {
        "name": character_name,
        "eye": sorted(eye_tags),
        "hair": sorted(hair_tags),
        "other": sorted(other_tags)
    }
    return {"character_tags": character_tags}


def get_query_result_count(
    query: str,
    api_key: str,
    user_id: str,
    limit: int = 100
) -> int:
    """
    Returns the number of results for a given Gelbooru search query.
    Args:
        query: Gelbooru search query (tags separated by spaces)
        api_key: Your Gelbooru API key
        user_id: Your Gelbooru user ID
        limit: Number of results per page (default: 100)
    Returns:
        Number of results found for the query
    """
    params = build_query_params(query, api_key, user_id, limit=limit)
    url = format_url(GELBOORU_API_BASE, params)
    try:
        data = ImageDownloader(".").get_json(url)
    except Exception as e:
        raise ScraperError(f"Failed to fetch result count: {e}")
    attributes = data.get("@attributes", {})
    return int(attributes.get("count", 0))