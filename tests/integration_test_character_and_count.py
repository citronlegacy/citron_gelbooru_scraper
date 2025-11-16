import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from citron_gelbooru_scraper.core import get_query_result_count, get_character_tags

# Hardcoded credentials (replace with valid ones for real test)
GELBOORU_API_KEY = "TODO_Replace_me"
GELBOORU_USER_ID = "TODO_Replace_me"

QUERY = "catgirl"
CHARACTER = "shantae"


def main():
    # Check for placeholder credentials
    if GELBOORU_API_KEY == "TODO_REPLACE_WITH_VALID_API_KEY" or GELBOORU_USER_ID == "TODO_REPLACE_WITH_VALID_USER_ID":
        raise Exception("Please update GELBOORU_API_KEY and GELBOORU_USER_ID with valid credentials before running the integration test.")

    print("Testing get_query_result_count...")
    count = get_query_result_count(QUERY, GELBOORU_API_KEY, GELBOORU_USER_ID)
    print(f"Result count for query '{QUERY}': {count}")
    assert isinstance(count, int), "Count should be an integer"
    assert count >= 1000, "Count should be non-negative"

    print("Testing get_character_tags...")
    result = get_character_tags(CHARACTER, GELBOORU_API_KEY, GELBOORU_USER_ID, max_images=50)
    print(f"Character tags for '{CHARACTER}': {result}")
    assert "character_tags" in result, "Result should contain 'character_tags' key"
    tags = result["character_tags"]
    assert isinstance(tags, dict), "character_tags should be a dict"
    assert "name" in tags and tags["name"] == CHARACTER, f"character_tags should contain correct name ('{CHARACTER}')"
    assert all(isinstance(tags[k], list) for k in ["eye", "hair", "other"]), "eye, hair, other should be lists"
    assert "purple hair" in tags["hair"], "'purple hair' should be in the hair tags"
    print("Integration test passed.")

if __name__ == "__main__":
    main()
