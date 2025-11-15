"""
Image and tag downloader module.

Handles downloading images and saving associated tags from Gelbooru.
"""

import json
import httpx
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.request import Request, urlopen

from citron_gelbooru_scraper.tags import extract_tags, clean_tags, get_default_blacklist
from citron_gelbooru_scraper.utils import (
    logger,
    ensure_dir_exists,
    sanitize_filename,
    rate_limit,
    retry_on_error,
    get_file_extension,
    DownloadError
)

USER_AGENT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/93.0.4577.83 Safari/537.36"


class ImageDownloader:
    """Handles downloading images and tags from Gelbooru."""
    
    def __init__(self, output_dir: str, blacklist: Optional[set] = None):
        """
        Initialize downloader.
        
        Args:
            output_dir: Directory to save images and tags
            blacklist: Optional set of tags to exclude
        """
        self.output_dir = ensure_dir_exists(output_dir)
        self.blacklist = blacklist or get_default_blacklist()
        self.supported_types = (".png", ".jpg", ".jpeg", ".gif", ".webp")
    
    @rate_limit(min_interval=0.1)
    def get_json(self, url: str) -> Dict[str, Any]:
        """
        Fetch JSON data from URL with rate limiting.
        
        Args:
            url: URL to fetch
            
        Returns:
            Parsed JSON data
            
        Raises:
            DownloadError: If request fails
        """
        try:
            logger.debug(f"Fetching JSON from: {url}")
            with urlopen(Request(url, headers={"User-Agent": USER_AGENT})) as page:
                return json.load(page)
        except Exception as e:
            raise DownloadError(f"Failed to fetch JSON: {e}")
    
    def save_tags(self, md5: str, tags: List[str]) -> Path:
        """
        Save tags to a text file.
        
        Args:
            md5: MD5 hash of the image (used as filename)
            tags: List of tags to save
            
        Returns:
            Path to the saved tags file
        """
        safe_md5 = sanitize_filename(md5)
        tags_file = self.output_dir / f"{safe_md5}.txt"
        cleaned_tags = clean_tags(tags, self.blacklist)
        
        with open(tags_file, "w", encoding="utf-8") as f:
            f.write(cleaned_tags)
        
        logger.debug(f"Saved tags to {tags_file}")
        return tags_file
    
    def parse_post(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a Gelbooru post and extract relevant data.
        
        Args:
            post: Post data from Gelbooru API
            
        Returns:
            Dictionary with image URL, MD5, tags, and post ID, or None if invalid
        """
        md5 = post.get("md5", "")
        if not md5:
            return None
        
        original_url = post.get("file_url", "")
        if not original_url:
            return None
        
        # Extract and clean tags
        tag_string = post.get("tags", "")
        tags = extract_tags(tag_string)
        
        # Filter blacklisted tags
        tags = [t for t in tags if t not in self.blacklist]
        
        return {
            "md5": md5,
            "url": original_url,
            "tags": tags,
            "post_id": post.get("id", ""),
        }
    
    @retry_on_error(max_retries=3, delay=1.0)
    def download_image(self, url: str, filename: str) -> Path:
        """
        Download an image from URL.
        
        Args:
            url: Image URL
            filename: Filename to save as (without extension)
            
        Returns:
            Path to downloaded image
            
        Raises:
            DownloadError: If download fails
        """
        try:
            ext = get_file_extension(url)            
            safe_filename = sanitize_filename(filename)
            filepath = self.output_dir / f"{safe_filename}{ext}"
            
            # Skip if already exists
            if filepath.exists():
                logger.debug(f"Image already exists: {filepath}")
                return filepath
            
            logger.debug(f"Downloading {url}")
            with httpx.stream("GET", url, follow_redirects=True, timeout=30.0) as response:
                response.raise_for_status()
                
                with open(filepath, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            
            logger.info(f"Downloaded: {filepath.name}")
            return filepath
            
        except Exception as e:
            raise DownloadError(f"Failed to download {url}: {e}")
    
    def process_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple posts and prepare download list.
        
        Args:
            posts: List of post data from Gelbooru
            
        Returns:
            List of parsed post data ready for download
        """
        processed = []
        
        for post in posts:
            parsed = self.parse_post(post)
            if parsed:
                # Save tags immediately
                self.save_tags(parsed["md5"], parsed["tags"])
                processed.append(parsed)
        
        return processed
    
    def download_batch(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Download a batch of images.
        
        Args:
            posts: List of parsed post data
            
        Returns:
            Summary with success/failure counts
        """
        results = {
            "downloaded": 0,
            "failed": 0,
            "errors": []
        }
        
        for post in posts:
            try:
                self.download_image(post["url"], post["md5"])
                results["downloaded"] += 1
            except DownloadError as e:
                results["failed"] += 1
                results["errors"].append(str(e))
                logger.error(f"Download failed: {e}")
        
        return results
