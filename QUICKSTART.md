# Quick Start Guide

Get up and running with Gelbooru Scraper in a few minutes!

## 1. Installation

```bash
# Navigate to project directory
cd /path/to/directory

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Get API Credentials

1. Log in to [Gelbooru](https://gelbooru.com/)
2. Go to [Account Options](https://gelbooru.com/index.php?page=account&s=options)
3. Generate an API key
4. Note your User ID

## 3. Basic Usage

```python
from gelbooru_scraper.core import jelly_download

# Download images
result = jelly_download(
    query="catgirl rating:general",
    api_key="YOUR_API_KEY",
    user_id="YOUR_USER_ID",
    output_dir="./downloads",
    max_images=50
)

print(f"Downloaded {result['downloaded']} images!")
```

## 4. Run Example

```bash
# Set environment variables
export GELBOORU_API_KEY="your_api_key_here"
export GELBOORU_USER_ID="your_user_id_here"

# Run example script
python example_usage.py
```

## 5. Query Tips

### Basic Syntax
- `catgirl` - Search for tag
- `cat dog` - Images with both tags
- `-animated` - Exclude animated images
- `rating:general` - SFW content only
- `rating:safe` - Also SFW
- `sort:score` - Sort by score

### Multi-word Tags
Use underscores: `shantae_(series)` or `long_hair`

### Example Queries
```python
# SFW cat girl images
"catgirl rating:general -animated sort:score"

# Specific character
"shantae_(series)"

# Landscape art
"landscape scenery no_humans rating:general"
```

## 6. Run Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=gelbooru_scraper --cov-report=html

# View coverage
open htmlcov/index.html
```

## Common Issues

### 401 Authentication Error
- Verify your API key and user ID are correct
- Check they're not wrapped in extra quotes

### No Results Found
- Check your query syntax
- Try searching on Gelbooru website first
- Remove restrictive filters

### Rate Limiting
- The library includes built-in rate limiting
- If you still hit limits, reduce `max_images`

## Project Structure

```
jelly_scraper/
├── gelbooru_scraper/      # Main package
│   ├── __init__.py        # Package exports
│   ├── auth.py            # Authentication
│   ├── core.py            # Main entrypoint
│   ├── downloader.py      # Download logic
│   ├── tags.py            # Tag processing
│   └── utils.py           # Utilities
├── tests/                 # Test suite
├── example_usage.py       # Usage example
├── requirements.txt       # Dependencies
└── README.md             # Full documentation
```

## Need Help?

- Read the [full README](README.md)
- Check [AppSpec](.copilot/AppSpec_Gelbooru_Scraper.md)
- Review [example code](.copilot/example_code.txt)
- See [Contributing Guidelines](CONTRIBUTING.md)
