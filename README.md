## Launch Downloader in Colab

[![Open in Colab](https://raw.githubusercontent.com/citronlegacy/kohya-colab/main/assets/colab-badge.svg)](https://colab.research.google.com/github/citronlegacy/citron_gelbooru_scraper/blob/main/citron_gelbooru_scraper_example.ipynb)
# Gelbooru Image & Tag Scraper

Python library to search Gelbooru using a query string, authenticate via API key/user ID, and download images plus tags for each result.

## Features

- Search Gelbooru with custom queries
- Authenticate using API key and user ID
- Download images and corresponding tags
- Robust error handling and rate limiting

## Requirements

- Python 3.11+
- Valid Gelbooru API key and user ID

## Installation

```bash
# Clone the repository
git clone https://github.com/citronlegacy/citron_gelbooru_scraper
cd jelly_scraper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
from citron_gelbooru_scraper.core import jelly_download

# Download images and tags
jelly_download(
  query="catgirl rating:safe",
  api_key="YOUR_API_KEY",
  user_id="YOUR_USER_ID",
  output_dir="./downloads"
)
```

### Query Format

Gelbooru uses tags separated by spaces. Use underscores for multi-word tags:
- `shantae_(series)` - Search for Shantae series
- `rating:general` - SFW content only
- `-animated` - Exclude animated content
- `sort:score` - Sort by score

### Authentication

Get your API credentials from [Gelbooru API Settings](https://gelbooru.com/index.php?page=account&s=options):
1. Log in to Gelbooru
2. Go to Account Options
3. Generate API key and note your user ID

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=citron_gelbooru_scraper --cov-report=html
```

## Project Structure

```
citron_gelbooru_scraper/
  __init__.py       # Package initialization
  core.py           # Main entrypoint (jelly_download)
  auth.py           # API authentication
  downloader.py     # Image and tag downloading
  tags.py           # Tag extraction and formatting
  utils.py          # Helper functions
tests/
  test_core.py      # Core functionality tests
  test_downloader.py # Downloader tests
  test_tags.py      # Tag processing tests
```


## API Reference

### `jelly_download(query, api_key, user_id, output_dir, max_images=100)`
Main function to search and download images from Gelbooru.

**Parameters:**
- `query` (str): Gelbooru search query with tags
- `api_key` (str): Your Gelbooru API key
- `user_id` (str): Your Gelbooru user ID
- `output_dir` (str): Directory to save images and tags
- `max_images` (int, optional): Maximum number of images to download (default: 100)

**Returns:**
- `dict`: Summary with downloaded count and any errors


### `get_query_result_count(query, api_key, user_id, limit=100)`
Returns the number of results for a given Gelbooru search query.

**Parameters:**
- `query` (str): Gelbooru search query with tags
- `api_key` (str): Your Gelbooru API key
- `user_id` (str): Your Gelbooru user ID
- `limit` (int, optional): Number of results per page (default: 100)

**Returns:**
- `int`: Number of results found for the query

**Example code:**
```python
from citron_gelbooru_scraper.core import get_query_result_count
count = get_query_result_count("catgirl", api_key, user_id)
print(f"Result count for 'catgirl': {count}")
```


### `get_character_tags(character_name, api_key, user_id, max_images=100)`
Extracts character tags (eye, hair, other) for a given character. It is hardcoded to only consider results for "solo rating:general sort:score" to avoid confusing tags in the results.

**Parameters:**
- `character_name` (str): Name of the character to search for
- `api_key` (str): Your Gelbooru API key
- `user_id` (str): Your Gelbooru user ID
- `max_images` (int, optional): Maximum number of images to analyze (default: 100)

**Returns:**
- `dict`: Dictionary containing structured character tags:
  - `character_tags` (dict):
    - `name` (str): Character name
    - `eye` (list): List of tags with the word "eye" in it
    - `hair` (list): List of tags with the word "hair" in it or specifically hardcoded hair tags: "ponytail", "twintails",    "braid", "ahoge", "two side up"
    - `other` (list): List of other top tags

**Example code:**
```python
from citron_gelbooru_scraper.core import get_character_tags
result = get_character_tags("shantae", api_key, user_id, max_images=50)
print(f"Character tags for 'shantae': {result}")
```

Example output:
```bash
Character tags for 'shantae': {'character_tags': {'name': 'shantae', 'eye': ['blue eyes'], 'hair': ['big hair', 'long hair', 'ponytail', 'purple hair', 'very long hair'], 'other': ['1girl', 'bandeau', 'bare shoulders', 'bracelet', 'bracer', ...]}}
```

## Security

- Never commit API keys to version control
- Use environment variables for credentials
- API keys are not logged

## License

MIT License

## References

- [Gelbooru API Documentation](https://gelbooru.com/index.php?page=wiki&s=view&id=18780)
- [AppSpec Documentation](.copilot/AppSpec_Gelbooru_Scraper.md)
