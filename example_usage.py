"""
Example usage of the Gelbooru scraper library.

This script demonstrates how to use the jelly_download function to search
and download images from Gelbooru.

Before running:
1. Get your API credentials from https://gelbooru.com/index.php?page=account&s=options
2. Set environment variables or replace the placeholders below
"""

import os
from pathlib import Path
from citron_gelbooru_scraper.core import jelly_download


def main():
    """Run example download."""
    
    # Get credentials from environment variables or set them here
    # NEVER commit actual credentials to version control!
    api_key = os.getenv("GELBOORU_API_KEY", "YOUR_API_KEY_HERE")
    user_id = os.getenv("GELBOORU_USER_ID", "YOUR_USER_ID_HERE")
    
    if api_key == "YOUR_API_KEY_HERE" or user_id == "YOUR_USER_ID_HERE":
        print("⚠️  Please set your Gelbooru API credentials!")
        print("Set environment variables:")
        print("  export GELBOORU_API_KEY='your_api_key'")
        print("  export GELBOORU_USER_ID='your_user_id'")
        return
    
    # Define search query
    # Use Gelbooru tag syntax:
    # - Spaces separate tags
    # - Use underscores for multi-word tags
    # - rating:general for SFW content
    # - Use minus sign to exclude tags
    query = "catgirl rating:general -animated sort:score"
    
    # Set output directory
    output_dir = Path("./downloads")
    
    # Maximum images to download
    max_images = 20
    
    print(f"🔍 Searching Gelbooru for: {query}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Max images: {max_images}")
    print()
    
    try:
        # Download images and tags
        result = jelly_download(
            query=query,
            api_key=api_key,
            user_id=user_id,
            output_dir=str(output_dir),
            max_images=max_images
        )
        
        # Print summary
        print("\n" + "="*50)
        print("📊 Download Summary")
        print("="*50)
        print(f"Query: {result['query']}")
        print(f"Total found: {result['total_found']}")
        print(f"Downloaded: {result['downloaded']}")
        print(f"Failed: {result['failed']}")
        print(f"Output: {result['output_dir']}")
        
        if result['errors']:
            print(f"\n⚠️  Errors ({len(result['errors'])}):")
            for error in result['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        print("\n✅ Download complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
