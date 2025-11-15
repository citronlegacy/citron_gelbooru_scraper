"""
Unit tests for downloader module.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from citron_gelbooru_scraper.downloader import ImageDownloader
from citron_gelbooru_scraper.utils import DownloadError


class TestImageDownloader:
    """Tests for ImageDownloader class."""
    
    def test_initialization(self, tmp_path):
        """Test downloader initialization."""
        downloader = ImageDownloader(str(tmp_path))
        
        assert downloader.output_dir == tmp_path
        assert downloader.blacklist is not None
        assert len(downloader.blacklist) > 0
    
    def test_parse_post_valid(self, tmp_path):
        """Test parsing a valid post."""
        downloader = ImageDownloader(str(tmp_path))
        
        post = {
            "md5": "abc123",
            "file_url": "http://example.com/image.jpg",
            "tags": "cat dog bird",
            "id": "12345"
        }
        
        result = downloader.parse_post(post)
        
        assert result is not None
        assert result["md5"] == "abc123"
        assert result["url"] == "http://example.com/image.jpg"
        assert "cat" in result["tags"]
        assert "dog" in result["tags"]
        assert result["post_id"] == "12345"
    
    def test_parse_post_missing_md5(self, tmp_path):
        """Test parsing post with missing MD5."""
        downloader = ImageDownloader(str(tmp_path))
        
        post = {
            "file_url": "http://example.com/image.jpg",
            "tags": "cat dog"
        }
        
        result = downloader.parse_post(post)
        assert result is None
    
    def test_parse_post_missing_url(self, tmp_path):
        """Test parsing post with missing URL."""
        downloader = ImageDownloader(str(tmp_path))
        
        post = {
            "md5": "abc123",
            "tags": "cat dog"
        }
        
        result = downloader.parse_post(post)
        assert result is None
    
    def test_save_tags(self, tmp_path):
        """Test saving tags to file."""
        downloader = ImageDownloader(str(tmp_path))
        
        tags = ["cat", "dog", "bird"]
        md5 = "test123"
        
        result = downloader.save_tags(md5, tags)
        
        assert result.exists()
        assert result.name == "test123.txt"
        
        # Read and verify content
        content = result.read_text()
        assert "cat" in content
        assert "dog" in content
    
    def test_process_posts(self, tmp_path):
        """Test processing multiple posts."""
        downloader = ImageDownloader(str(tmp_path))
        
        posts = [
            {"md5": "abc", "file_url": "http://example.com/1.jpg", "tags": "cat", "id": "1"},
            {"md5": "def", "file_url": "http://example.com/2.jpg", "tags": "dog", "id": "2"},
            {"file_url": "http://example.com/3.jpg", "tags": "bird", "id": "3"},  # Missing MD5
        ]
        
        result = downloader.process_posts(posts)
        
        # Should only process posts with valid data
        assert len(result) == 2
        assert result[0]["md5"] == "abc"
        assert result[1]["md5"] == "def"
    
    @patch("citron_gelbooru_scraper.downloader.httpx.stream")
    def test_download_image_success(self, mock_stream, tmp_path):
        """Test successful image download."""
        downloader = ImageDownloader(str(tmp_path))
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.iter_bytes.return_value = [b"fake image data"]
        mock_response.raise_for_status = Mock()
        mock_stream.return_value.__enter__.return_value = mock_response
        
        result = downloader.download_image("http://example.com/test.jpg", "test123")
        
        assert result.exists()
        assert result.name == "test123.jpg"
    
    def test_download_batch(self, tmp_path):
        """Test downloading a batch of images."""
        downloader = ImageDownloader(str(tmp_path))
        
        # Mock the download_image method
        with patch.object(downloader, 'download_image') as mock_download:
            mock_download.return_value = tmp_path / "test.jpg"
            
            posts = [
                {"md5": "abc", "url": "http://example.com/1.jpg", "tags": ["cat"], "post_id": "1"},
                {"md5": "def", "url": "http://example.com/2.jpg", "tags": ["dog"], "post_id": "2"},
            ]
            
            result = downloader.download_batch(posts)
            
            assert result["downloaded"] == 2
            assert result["failed"] == 0
            assert mock_download.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
