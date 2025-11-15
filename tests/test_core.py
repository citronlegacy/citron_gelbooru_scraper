"""
Unit tests for core module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from citron_gelbooru_scraper.core import (
    jelly_download,
    build_query_params,
    GELBOORU_API_BASE,
    DEFAULT_LIMIT
)
from citron_gelbooru_scraper.utils import AuthenticationError, ScraperError


class TestBuildQueryParams:
    """Tests for build_query_params function."""
    
    def test_basic_params(self):
        """Test basic parameter building."""
        params = build_query_params(
            tags="catgirl",
            api_key="test_key",
            user_id="12345",
            limit=100,
            page=0
        )
        
        assert params["page"] == "dapi"
        assert params["s"] == "post"
        assert params["q"] == "index"
        assert params["json"] == "1"
        assert params["api_key"] == "test_key"
        assert params["user_id"] == "12345"
        assert params["tags"] == "catgirl"
        assert params["limit"] == "100"
        assert "pid" not in params
    
    def test_with_page_number(self):
        """Test params with page number."""
        params = build_query_params(
            tags="test",
            api_key="key",
            user_id="123",
            page=2
        )
        
        assert params["pid"] == "2"


class TestJellyDownload:
    """Tests for main jelly_download function."""
    
    @patch("citron_gelbooru_scraper.core.validate_credentials")
    @patch("citron_gelbooru_scraper.core.ImageDownloader")
    def test_invalid_credentials(self, mock_downloader, mock_validate):
        """Test behavior with invalid credentials."""
        mock_validate.side_effect = ValueError("Invalid credentials")
        
        with pytest.raises(AuthenticationError):
            jelly_download(
                query="test",
                api_key="bad_key",
                user_id="bad_id",
                output_dir="/tmp/test"
            )
    
    @patch("citron_gelbooru_scraper.core.validate_credentials")
    @patch("citron_gelbooru_scraper.core.ImageDownloader")
    def test_no_results(self, mock_downloader_class, mock_validate):
        """Test behavior when no results are found."""
        # Mock authentication
        mock_validate.return_value = Mock()
        
        # Mock downloader
        mock_downloader = Mock()
        mock_downloader.get_json.return_value = {
            "@attributes": {"count": 0},
            "post": []
        }
        mock_downloader_class.return_value = mock_downloader
        
        result = jelly_download(
            query="nonexistent_tag",
            api_key="test_key",
            user_id="12345",
            output_dir="/tmp/test"
        )
        
        assert result["total_found"] == 0
        assert result["downloaded"] == 0
        assert result["query"] == "nonexistent_tag"
    
    @patch("citron_gelbooru_scraper.core.validate_credentials")
    @patch("citron_gelbooru_scraper.core.ImageDownloader")
    def test_successful_download(self, mock_downloader_class, mock_validate):
        """Test successful download process."""
        # Mock authentication
        mock_validate.return_value = Mock()
        
        # Mock downloader
        mock_downloader = Mock()
        mock_downloader.get_json.return_value = {
            "@attributes": {"count": 2},
            "post": [
                {"md5": "abc123", "file_url": "http://example.com/1.jpg", "tags": "cat dog", "id": "1"},
                {"md5": "def456", "file_url": "http://example.com/2.jpg", "tags": "bird", "id": "2"}
            ]
        }
        mock_downloader.process_posts.return_value = [
            {"md5": "abc123", "url": "http://example.com/1.jpg", "tags": ["cat", "dog"], "post_id": "1"},
            {"md5": "def456", "url": "http://example.com/2.jpg", "tags": ["bird"], "post_id": "2"}
        ]
        mock_downloader.download_batch.return_value = {
            "downloaded": 2,
            "failed": 0,
            "errors": []
        }
        mock_downloader_class.return_value = mock_downloader
        
        result = jelly_download(
            query="animal",
            api_key="test_key",
            user_id="12345",
            output_dir="/tmp/test",
            max_images=2
        )
        
        assert result["total_found"] == 2
        assert result["downloaded"] == 2
        assert result["failed"] == 0
        assert len(result["errors"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
