## Launch in Colab

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

## Security

- Never commit API keys to version control
- Use environment variables for credentials
- API keys are not logged

## License

MIT License

## References

- [Gelbooru API Documentation](https://gelbooru.com/index.php?page=wiki&s=view&id=18780)
- [AppSpec Documentation](.copilot/AppSpec_Gelbooru_Scraper.md)
