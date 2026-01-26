"""Tests for PageRangers SEO API client."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from pagerangers import (
    call_endpoint,
    get_by_path,
    load_config,
    normalize_competition,
    normalize_urls,
    substitute,
)


class TestSubstitute:
    """Tests for placeholder substitution."""

    def test_substitute_string(self):
        """Substitute placeholders in string."""
        result = substitute("{api_token}", {"api_token": "secret123"})
        assert result == "secret123"

    def test_substitute_multiple_placeholders(self):
        """Substitute multiple placeholders."""
        template = "token={api_token}&hash={project_hash}"
        variables = {"api_token": "abc", "project_hash": "xyz"}
        result = substitute(template, variables)
        assert result == "token=abc&hash=xyz"

    def test_substitute_dict(self):
        """Substitute placeholders in dictionary."""
        template = {"key": "{value}", "other": "static"}
        result = substitute(template, {"value": "dynamic"})
        assert result == {"key": "dynamic", "other": "static"}

    def test_substitute_list(self):
        """Substitute placeholders in list."""
        template = ["{a}", "{b}", "c"]
        result = substitute(template, {"a": "x", "b": "y"})
        assert result == ["x", "y", "c"]

    def test_substitute_non_string(self):
        """Non-string values returned unchanged."""
        assert substitute(123, {"x": "y"}) == 123
        assert substitute(None, {"x": "y"}) is None


class TestGetByPath:
    """Tests for nested dictionary path extraction."""

    def test_simple_path(self):
        """Extract value with simple path."""
        data = {"keyword": "test"}
        assert get_by_path(data, "keyword") == "test"

    def test_nested_path(self):
        """Extract value with nested path."""
        data = {"data": {"keyword": "nested"}}
        assert get_by_path(data, "data.keyword") == "nested"

    def test_array_index(self):
        """Extract value with array index."""
        data = {"items": [{"name": "first"}, {"name": "second"}]}
        assert get_by_path(data, "items[0].name") == "first"
        assert get_by_path(data, "items[1].name") == "second"

    def test_missing_key(self):
        """Return None for missing key."""
        data = {"a": "b"}
        assert get_by_path(data, "missing") is None

    def test_empty_path(self):
        """Empty path returns original data."""
        data = {"key": "value"}
        assert get_by_path(data, "") == data


class TestNormalizeUrls:
    """Tests for URL extraction from SERP results."""

    def test_extract_urls_from_dict_list(self):
        """Extract URLs from list of dicts."""
        serp = [{"url": "https://a.com"}, {"url": "https://b.com"}]
        result = normalize_urls(serp)
        assert result == ["https://a.com", "https://b.com"]

    def test_extract_urls_with_limit(self):
        """Limit number of URLs returned."""
        serp = [{"url": f"https://{i}.com"} for i in range(10)]
        result = normalize_urls(serp, limit=3)
        assert len(result) == 3

    def test_extract_urls_different_keys(self):
        """Extract URLs from different key names."""
        serp = [{"link": "https://a.com"}, {"href": "https://b.com"}]
        result = normalize_urls(serp)
        assert result == ["https://a.com", "https://b.com"]

    def test_extract_urls_from_strings(self):
        """Handle list of plain strings."""
        serp = ["https://a.com", "https://b.com"]
        result = normalize_urls(serp)
        assert result == ["https://a.com", "https://b.com"]

    def test_non_list_returns_empty(self):
        """Non-list input returns empty list."""
        assert normalize_urls(None) == []
        assert normalize_urls("string") == []


class TestNormalizeCompetition:
    """Tests for competition score normalization."""

    def test_low_competition(self):
        """Values <= 0.33 are low."""
        assert normalize_competition(0.1) == "low"
        assert normalize_competition(0.33) == "low"

    def test_medium_competition(self):
        """Values 0.33-0.66 are medium."""
        assert normalize_competition(0.5) == "medium"
        assert normalize_competition(0.66) == "medium"

    def test_high_competition(self):
        """Values > 0.66 are high."""
        assert normalize_competition(0.7) == "high"
        assert normalize_competition(1.0) == "high"

    def test_none_returns_unknown(self):
        """None value returns unknown."""
        assert normalize_competition(None) == "unknown"

    def test_string_passthrough(self):
        """String values passed through."""
        assert normalize_competition("custom") == "custom"


class TestLoadConfig:
    """Tests for configuration loading."""

    def test_load_config_success(self, config_path):
        """Successfully load config file."""
        config = load_config(config_path)
        assert "base_url" in config
        assert "endpoints" in config
        assert "keyword" in config["endpoints"]

    def test_config_has_required_endpoints(self, api_config):
        """Config has all required endpoints."""
        endpoints = api_config["endpoints"]
        assert "keyword" in endpoints
        assert "rankings" in endpoints
        assert "main_kpis" in endpoints
        assert "prospects" in endpoints


class TestCallEndpoint:
    """Tests for API endpoint calls."""

    def test_call_endpoint_success(self, mock_env, api_config, mock_kpis_response):
        """Successfully call an endpoint."""
        with patch("pagerangers.request_json") as mock_request:
            mock_request.return_value = mock_kpis_response

            result = call_endpoint(
                api_config,
                "main_kpis",
                {"api_token": "test", "project_hash": "ABC"},
                timeout=30,
            )

            assert result == mock_kpis_response
            mock_request.assert_called_once()

    def test_call_endpoint_unknown_endpoint(self, mock_env, api_config):
        """Raise error for unknown endpoint."""
        with pytest.raises(RuntimeError, match="Unknown endpoint"):
            call_endpoint(
                api_config,
                "nonexistent",
                {"api_token": "test", "project_hash": "ABC"},
                timeout=30,
            )

    def test_call_endpoint_api_error(self, mock_env, api_config, mock_error_response):
        """Handle API-level error in response."""
        with patch("pagerangers.request_json") as mock_request:
            mock_request.return_value = mock_error_response

            with pytest.raises(RuntimeError, match="API Error"):
                call_endpoint(
                    api_config,
                    "main_kpis",
                    {"api_token": "test", "project_hash": "ABC"},
                    timeout=30,
                )


class TestCLICommands:
    """Integration tests for CLI commands."""

    def test_kpis_command_json_output(self, mock_env, mock_kpis_response):
        """Test kpis command with JSON output."""
        with patch("pagerangers.call_endpoint") as mock_call:
            mock_call.return_value = mock_kpis_response

            # Import cmd_kpis after patching
            from pagerangers import cmd_kpis

            # Create mock args
            args = MagicMock()
            args.json = True
            args.debug = False

            # Capture stdout
            captured = StringIO()
            with patch("sys.stdout", captured):
                result = cmd_kpis(
                    args,
                    {"endpoints": {"main_kpis": {"response": {
                        "ranking_index": "rankingindex",
                        "top_10_count": "numberOfKeywordsInTop10",
                        "top_100_count": "numberOfKeywordsTop100",
                        "average_position": "averageTopPosition",
                    }}}},
                    {"api_token": "test", "project_hash": "ABC"},
                    timeout=30,
                )

            assert result == 0
            output = json.loads(captured.getvalue())
            assert "ranking_index" in output

    def test_rankings_command(self, mock_env, mock_rankings_response):
        """Test rankings command."""
        with patch("pagerangers.call_endpoint") as mock_call:
            mock_call.return_value = mock_rankings_response

            from pagerangers import cmd_rankings

            args = MagicMock()
            args.json = True
            args.debug = False
            args.limit = 10

            captured = StringIO()
            with patch("sys.stdout", captured):
                result = cmd_rankings(
                    args,
                    {"endpoints": {"rankings": {"response": {"keywords": "rankings"}}}},
                    {"api_token": "test", "project_hash": "ABC"},
                    timeout=30,
                )

            assert result == 0
            output = json.loads(captured.getvalue())
            assert "rankings" in output
            assert len(output["rankings"]) == 2

    def test_keyword_command(self, mock_env, mock_keyword_response):
        """Test keyword command."""
        with patch("pagerangers.call_endpoint") as mock_call:
            mock_call.return_value = mock_keyword_response

            from pagerangers import cmd_keyword

            args = MagicMock()
            args.json = True
            args.debug = False
            args.keyword = "SEO tools"
            args.top = 5

            captured = StringIO()
            with patch("sys.stdout", captured):
                result = cmd_keyword(
                    args,
                    {"endpoints": {"keyword": {"response": {
                        "main_keyword": "keyword",
                        "search_volume": "searchVolume",
                        "competition": "competition",
                        "top_urls": "serp",
                        "important_keywords": "relatedKeywords",
                    }}}},
                    {"api_token": "test", "project_hash": "ABC"},
                    timeout=30,
                )

            assert result == 0
            output = json.loads(captured.getvalue())
            assert output["main_keyword"] == "SEO tools"
            assert output["search_volume"] == 12100


class TestErrorHandling:
    """Tests for error handling."""

    def test_http_401_error(self, mock_env, api_config):
        """Handle 401 authentication error."""
        import urllib.error
        from io import BytesIO

        with patch("pagerangers.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://test.com",
                code=401,
                msg="Unauthorized",
                hdrs={},
                fp=BytesIO(b"Unauthorized"),
            )

            from pagerangers import request_json

            with pytest.raises(RuntimeError, match="Authentication failed"):
                request_json("GET", "http://test.com", {}, None, 30)

    def test_http_429_rate_limit(self, mock_env, api_config):
        """Handle 429 rate limit error."""
        import urllib.error
        from io import BytesIO

        with patch("pagerangers.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://test.com",
                code=429,
                msg="Too Many Requests",
                hdrs={},
                fp=BytesIO(b"Rate limited"),
            )

            from pagerangers import request_json

            with pytest.raises(RuntimeError, match="Rate limit exceeded"):
                request_json("GET", "http://test.com", {}, None, 30)
