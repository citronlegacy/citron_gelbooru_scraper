"""
Tag extraction and formatting module.

Handles parsing, cleaning, and formatting of image tags from Gelbooru.
"""

import html
from typing import List, Set, Optional
from collections import Counter


def extract_tags(tag_string: str) -> List[str]:
    """
    Extract and decode tags from raw tag string.
    
    Args:
        tag_string: Raw tag string from Gelbooru API
        
    Returns:
        List of cleaned tag strings
    """
    # Decode HTML entities
    decoded = html.unescape(tag_string)
    
    # Remove quotes and split on whitespace
    tags = decoded.replace("'", "").split()
    
    return tags


def filter_tags(tags: List[str], blacklist: Set[str]) -> List[str]:
    """
    Filter out blacklisted tags.
    
    Args:
        tags: List of tags to filter
        blacklist: Set of tags to exclude
        
    Returns:
        Filtered list of tags
    """
    return [tag for tag in tags if tag not in blacklist]


def format_tags(tags: List[str], use_underscores: bool = True) -> str:
    """
    Format tags for saving to file.
    
    Args:
        tags: List of tags to format
        use_underscores: If True, keep underscores; if False, replace with spaces
        
    Returns:
        Comma-separated tag string
    """
    if not use_underscores:
        # Replace underscores with spaces for tags longer than 3 characters
        tags = [tag.replace("_", " ") if len(tag) > 3 else tag for tag in tags]
    
    return ", ".join(tags)


def get_default_blacklist() -> Set[str]:
    """
    Get default set of tags to exclude.
    
    Returns:
        Set of blacklisted tags
    """
    return {
        "game_freak",
        "tagme",
        "creatures_(company)",
        "commentary_request",
        "commentary",
        "english_commentary",
        "symbol-only_commentary",
        "translation_request",
        "translated",
        "bad_pixiv_id",
        "bad_id",
        "skeb_commission",
        "commission",
    }


def clean_tags(tags: List[str], blacklist: Optional[Set[str]] = None) -> str:
    """
    Clean and format tags in one step.
    
    Args:
        tags: Raw list of tags
        blacklist: Optional set of tags to exclude (uses default if None)
        
    Returns:
        Formatted, cleaned tag string
    """
    if blacklist is None:
        blacklist = get_default_blacklist()
    
    filtered = filter_tags(tags, blacklist)
    return format_tags(filtered, use_underscores=False)


def count_tags(tag_files: List[str]) -> Counter:
    """
    Count tag frequencies across multiple tag files.
    
    Args:
        tag_files: List of paths to tag files
        
    Returns:
        Counter object with tag frequencies
    """
    tag_counter = Counter()
    
    for tag_file in tag_files:
        try:
            with open(tag_file, 'r') as f:
                tags = [t.strip() for t in f.read().split(",")]
                tag_counter.update(tags)
        except Exception:
            # Skip files that can't be read
            continue
    
    return tag_counter
