import os
import sys
from pathlib import Path
from citron_gelbooru_scraper.core import jelly_download

# Hardcoded credentials (replace with valid ones for real test)

GELBOORU_API_KEY = "TODO_REPLACE_WITH_VALID_API_KEY"
GELBOORU_USER_ID = "TODO_REPLACE_WITH_VALID_USER_ID"

QUERY = "catgirl -animated"
MAX_IMAGES = 5
OUTPUT_DIR = Path("./integration_test_downloads")

def main():
    # Check for placeholder credentials
    if GELBOORU_API_KEY == "TODO_REPLACE_WITH_VALID_API_KEY" or GELBOORU_USER_ID == "TODO_REPLACE_WITH_VALID_USER_ID":
        raise Exception("Please update GELBOORU_API_KEY and GELBOORU_USER_ID with valid credentials before running the integration test.")

    # Clean output dir before test
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.iterdir():
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                for subf in f.iterdir():
                    subf.unlink()
                f.rmdir()
    else:
        OUTPUT_DIR.mkdir(parents=True)

    result = jelly_download(
        query=QUERY,
        api_key=GELBOORU_API_KEY,
        user_id=GELBOORU_USER_ID,
        output_dir=str(OUTPUT_DIR),
        max_images=MAX_IMAGES
    )

    # Check images and tag files
    image_files = [f for f in OUTPUT_DIR.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")]
    tag_files = [f for f in OUTPUT_DIR.iterdir() if f.suffix == ".txt"]

    assert len(image_files) == MAX_IMAGES, f"Expected {MAX_IMAGES} images, found {len(image_files)}"
    assert len(tag_files) == MAX_IMAGES, f"Expected {MAX_IMAGES} tag files, found {len(tag_files)}"
    print("Integration test passed: 5 images and 5 tag files downloaded.")

if __name__ == "__main__":
    main()
