"""
Unit tests for tags module.
"""

import pytest
from collections import Counter

from citron_gelbooru_scraper.tags import (
    extract_tags,
    filter_tags,
    format_tags,
    get_default_blacklist,
    clean_tags
)


class TestExtractTags:
    """Tests for extract_tags function."""
    
    def test_basic_extraction(self):
        """Test extracting tags from basic string."""
        tag_string = "cat dog bird"
        result = extract_tags(tag_string)
        
        assert result == ["cat", "dog", "bird"]
    
    def test_html_entity_decoding(self):
        """Test HTML entity decoding."""
        tag_string = "cat &amp; dog"
        result = extract_tags(tag_string)
        
        assert "cat" in result
        assert "&" in result
        assert "dog" in result
    
    def test_removes_quotes(self):
        """Test removal of quotes."""
        tag_string = "'cat' 'dog'"
        result = extract_tags(tag_string)
        
        assert result == ["cat", "dog"]


class TestFilterTags:
    """Tests for filter_tags function."""
    
    def test_basic_filtering(self):
        """Test filtering with blacklist."""
        tags = ["cat", "dog", "tagme", "bird"]
        blacklist = {"tagme", "commentary"}
        
        result = filter_tags(tags, blacklist)
        
        assert "cat" in result
        assert "dog" in result
        assert "bird" in result
        assert "tagme" not in result
    
    def test_empty_blacklist(self):
        """Test with empty blacklist."""
        tags = ["cat", "dog", "bird"]
        blacklist = set()
        
        result = filter_tags(tags, blacklist)
        
        assert len(result) == 3
        assert result == tags


class TestFormatTags:
    """Tests for format_tags function."""
    
    def test_with_underscores(self):
        """Test formatting with underscores preserved."""
        tags = ["cat_girl", "long_hair", "red"]
        result = format_tags(tags, use_underscores=True)
        
        assert result == "cat_girl, long_hair, red"
    
    def test_without_underscores(self):
        """Test formatting with underscores replaced."""
        tags = ["cat_girl", "long_hair", "red"]
        result = format_tags(tags, use_underscores=False)
        
        # Should replace underscores in tags > 3 chars
        assert "cat girl" in result
        assert "long hair" in result
        assert "red" in result
    
    def test_short_tags_keep_underscores(self):
        """Test that short tags keep underscores."""
        tags = ["a_b", "red"]
        result = format_tags(tags, use_underscores=False)
        
        # Short tag should keep underscore
        assert "a_b" in result


class TestGetDefaultBlacklist:
    """Tests for get_default_blacklist function."""
    
    def test_returns_set(self):
        """Test that it returns a set."""
        result = get_default_blacklist()
        
        assert isinstance(result, set)
        assert len(result) > 0
    
    def test_contains_common_tags(self):
        """Test that blacklist contains expected tags."""
        result = get_default_blacklist()
        
        assert "tagme" in result
        assert "commentary" in result
        assert "translated" in result


class TestCleanTags:
    """Tests for clean_tags function."""
    
    def test_cleans_and_formats(self):
        """Test that it cleans and formats tags."""
        tags = ["cat_girl", "tagme", "long_hair", "commentary"]
        result = clean_tags(tags)
        
        # Should remove blacklisted tags
        assert "tagme" not in result
        assert "commentary" not in result
        
        # Should format remaining tags
        assert "cat girl" in result or "cat_girl" in result
    
    def test_custom_blacklist(self):
        """Test with custom blacklist."""
        tags = ["cat", "dog", "bird", "custom_tag"]
        blacklist = {"custom_tag"}
        
        result = clean_tags(tags, blacklist)
        
        assert "cat" in result
        assert "dog" in result
        assert "custom_tag" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
