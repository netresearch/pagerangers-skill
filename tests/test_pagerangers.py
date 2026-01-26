"""Tests for PageRangers SEO API client."""

from __future__ import annotations

import json
import sys
import urllib.error
from io import BytesIO, StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from pagerangers import (
    COMPETITION_LOW_THRESHOLD,
    COMPETITION_MEDIUM_THRESHOLD,
    DEFAULT_LIMIT,
    DEFAULT_TIMEOUT,
    DEFAULT_TOP_URLS,
    HTTP_FORBIDDEN,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_UNAUTHORIZED,
    MAX_RELATED_KEYWORDS,
    CommandContext,
    call_endpoint,
    cmd_keyword,
    cmd_kpis,
    cmd_rankings,
    get_by_path,
    load_config,
    normalize_competition,
    normalize_urls,
    request_json,
    substitute,
)

# Test constants
EXIT_SUCCESS = 0
EXPECTED_RANKINGS_COUNT = 2
EXPECTED_SEARCH_VOLUME = 12100


class TestConstants:
    """Tests for module constants."""

    def test_http_status_codes_are_4xx(self) -> None:
        """Verify HTTP status codes are in 4xx client error range."""
        for code in (HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_TOO_MANY_REQUESTS):
            assert isinstance(code, int)
            assert code >= HTTP_UNAUTHORIZED  # All should be >= 401

    def test_competition_thresholds_are_ordered(self) -> None:
        """Verify competition thresholds are properly ordered."""
        assert isinstance(COMPETITION_LOW_THRESHOLD, float)
        assert isinstance(COMPETITION_MEDIUM_THRESHOLD, float)
        assert COMPETITION_LOW_THRESHOLD < COMPETITION_MEDIUM_THRESHOLD

    def test_default_values_are_positive(self) -> None:
        """Verify default values are positive integers."""
        for value in (DEFAULT_TIMEOUT, DEFAULT_TOP_URLS, DEFAULT_LIMIT, MAX_RELATED_KEYWORDS):
            assert isinstance(value, int)
            assert value > 0


class TestSubstitute:
    """Tests for placeholder substitution."""

    def test_substitute_string(self) -> None:
        """Substitute placeholders in string."""
        result = substitute("{api_token}", {"api_token": "secret123"})
        assert result == "secret123"

    def test_substitute_multiple_placeholders(self) -> None:
        """Substitute multiple placeholders."""
        template = "token={api_token}&hash={project_hash}"
        variables = {"api_token": "abc", "project_hash": "xyz"}
        result = substitute(template, variables)
        assert result == "token=abc&hash=xyz"

    def test_substitute_dict(self) -> None:
        """Substitute placeholders in dictionary."""
        template = {"key": "{value}", "other": "static"}
        result = substitute(template, {"value": "dynamic"})
        assert result == {"key": "dynamic", "other": "static"}

    def test_substitute_list(self) -> None:
        """Substitute placeholders in list."""
        template = ["{a}", "{b}", "c"]
        result = substitute(template, {"a": "x", "b": "y"})
        assert result == ["x", "y", "c"]

    def test_substitute_non_string(self) -> None:
        """Non-string values returned unchanged."""
        assert substitute(None, {"x": "y"}) is None


class TestGetByPath:
    """Tests for nested dictionary path extraction."""

    def test_simple_path(self) -> None:
        """Extract value with simple path."""
        data = {"keyword": "test"}
        assert get_by_path(data, "keyword") == "test"

    def test_nested_path(self) -> None:
        """Extract value with nested path."""
        data = {"data": {"keyword": "nested"}}
        assert get_by_path(data, "data.keyword") == "nested"

    def test_array_index(self) -> None:
        """Extract value with array index."""
        data = {"items": [{"name": "first"}, {"name": "second"}]}
        assert get_by_path(data, "items[0].name") == "first"
        assert get_by_path(data, "items[1].name") == "second"

    def test_missing_key(self) -> None:
        """Return None for missing key."""
        data = {"a": "b"}
        assert get_by_path(data, "missing") is None

    def test_empty_path(self) -> None:
        """Empty path returns original data."""
        data = {"key": "value"}
        assert get_by_path(data, "") == data


class TestNormalizeUrls:
    """Tests for URL extraction from SERP results."""

    def test_extract_urls_from_dict_list(self) -> None:
        """Extract URLs from list of dicts."""
        serp = [{"url": "https://a.com"}, {"url": "https://b.com"}]
        result = normalize_urls(serp)
        assert result == ["https://a.com", "https://b.com"]

    def test_extract_urls_with_limit(self) -> None:
        """Limit number of URLs returned."""
        url_limit = 3
        serp = [{"url": f"https://{i}.com"} for i in range(10)]
        result = normalize_urls(serp, limit=url_limit)
        assert len(result) == url_limit

    def test_extract_urls_different_keys(self) -> None:
        """Extract URLs from different key names."""
        serp = [{"link": "https://a.com"}, {"href": "https://b.com"}]
        result = normalize_urls(serp)
        assert result == ["https://a.com", "https://b.com"]

    def test_extract_urls_from_strings(self) -> None:
        """Handle list of plain strings."""
        serp = ["https://a.com", "https://b.com"]
        result = normalize_urls(serp)
        assert result == ["https://a.com", "https://b.com"]

    def test_non_list_returns_empty(self) -> None:
        """Non-list input returns empty list."""
        assert normalize_urls(None) == []


class TestNormalizeCompetition:
    """Tests for competition score normalization."""

    def test_low_competition(self) -> None:
        """Values <= threshold are low."""
        assert normalize_competition(0.1) == "low"
        assert normalize_competition(COMPETITION_LOW_THRESHOLD) == "low"

    def test_medium_competition(self) -> None:
        """Values between thresholds are medium."""
        assert normalize_competition(0.5) == "medium"
        assert normalize_competition(COMPETITION_MEDIUM_THRESHOLD) == "medium"

    def test_high_competition(self) -> None:
        """Values > medium threshold are high."""
        assert normalize_competition(0.7) == "high"
        assert normalize_competition(1.0) == "high"

    def test_none_returns_unknown(self) -> None:
        """None value returns unknown."""
        assert normalize_competition(None) == "unknown"

    def test_string_passthrough(self) -> None:
        """String values passed through."""
        assert normalize_competition("custom") == "custom"


class TestLoadConfig:
    """Tests for configuration loading."""

    def test_load_config_success(self, config_path: Path) -> None:
        """Successfully load config file."""
        config = load_config(config_path)
        assert "base_url" in config
        assert "endpoints" in config
        assert "keyword" in config["endpoints"]

    def test_config_has_required_endpoints(self, api_config: dict) -> None:
        """Config has all required endpoints."""
        endpoints = api_config["endpoints"]
        assert "keyword" in endpoints
        assert "rankings" in endpoints
        assert "main_kpis" in endpoints
        assert "prospects" in endpoints


class TestCommandContext:
    """Tests for CommandContext dataclass."""

    def test_create_context(self) -> None:
        """Create command context with all fields."""
        ctx = CommandContext(
            config={"endpoints": {}},
            variables={"api_token": "test"},
            timeout=DEFAULT_TIMEOUT,
            debug=False,
        )
        assert ctx.config == {"endpoints": {}}
        assert ctx.variables == {"api_token": "test"}
        assert ctx.timeout == DEFAULT_TIMEOUT
        assert ctx.debug is False


class TestCallEndpoint:
    """Tests for API endpoint calls."""

    def test_call_endpoint_success(self, api_config: dict, mock_kpis_response: dict) -> None:
        """Successfully call an endpoint."""
        ctx = CommandContext(
            config=api_config,
            variables={"api_token": "test", "project_hash": "ABC"},
            timeout=DEFAULT_TIMEOUT,
            debug=False,
        )

        with patch("pagerangers.request_json") as mock_request:
            mock_request.return_value = mock_kpis_response
            result = call_endpoint(ctx, "main_kpis")

            assert result == mock_kpis_response
            mock_request.assert_called_once()

    def test_call_endpoint_unknown_endpoint(self, api_config: dict) -> None:
        """Raise error for unknown endpoint."""
        ctx = CommandContext(
            config=api_config,
            variables={"api_token": "test", "project_hash": "ABC"},
            timeout=DEFAULT_TIMEOUT,
            debug=False,
        )

        with pytest.raises(RuntimeError, match="Unknown endpoint"):
            call_endpoint(ctx, "nonexistent")

    def test_call_endpoint_api_error(self, api_config: dict, mock_error_response: dict) -> None:
        """Handle API-level error in response."""
        ctx = CommandContext(
            config=api_config,
            variables={"api_token": "test", "project_hash": "ABC"},
            timeout=DEFAULT_TIMEOUT,
            debug=False,
        )

        with patch("pagerangers.request_json") as mock_request:
            mock_request.return_value = mock_error_response

            with pytest.raises(RuntimeError, match="API Error"):
                call_endpoint(ctx, "main_kpis")


class TestCLICommands:
    """Integration tests for CLI commands."""

    def test_kpis_command_json_output(self, mock_kpis_response: dict) -> None:
        """Test kpis command with JSON output."""
        ctx = CommandContext(
            config={
                "endpoints": {
                    "main_kpis": {
                        "response": {
                            "ranking_index": "rankingindex",
                            "top_10_count": "numberOfKeywordsInTop10",
                            "top_100_count": "numberOfKeywordsTop100",
                            "average_position": "averageTopPosition",
                        }
                    }
                }
            },
            variables={"api_token": "test", "project_hash": "ABC"},
            timeout=DEFAULT_TIMEOUT,
            debug=False,
        )

        with patch("pagerangers.call_endpoint") as mock_call:
            mock_call.return_value = mock_kpis_response

            args = MagicMock()
            args.json = True

            captured = StringIO()
            with patch("sys.stdout", captured):
                result = cmd_kpis(args, ctx)

            assert result == EXIT_SUCCESS
            output = json.loads(captured.getvalue())
            assert "ranking_index" in output

    def test_rankings_command(self, mock_rankings_response: dict) -> None:
        """Test rankings command."""
        ctx = CommandContext(
            config={"endpoints": {"rankings": {"response": {"keywords": "rankings"}}}},
            variables={"api_token": "test", "project_hash": "ABC"},
            timeout=DEFAULT_TIMEOUT,
            debug=False,
        )

        with patch("pagerangers.call_endpoint") as mock_call:
            mock_call.return_value = mock_rankings_response

            args = MagicMock()
            args.json = True
            args.limit = DEFAULT_LIMIT

            captured = StringIO()
            with patch("sys.stdout", captured):
                result = cmd_rankings(args, ctx)

            assert result == EXIT_SUCCESS
            output = json.loads(captured.getvalue())
            assert "rankings" in output
            assert len(output["rankings"]) == EXPECTED_RANKINGS_COUNT

    def test_keyword_command(self, mock_keyword_response: dict) -> None:
        """Test keyword command."""
        ctx = CommandContext(
            config={
                "endpoints": {
                    "keyword": {
                        "response": {
                            "main_keyword": "keyword",
                            "search_volume": "searchVolume",
                            "competition": "competition",
                            "top_urls": "serp",
                            "important_keywords": "relatedKeywords",
                        }
                    }
                }
            },
            variables={"api_token": "test", "project_hash": "ABC"},
            timeout=DEFAULT_TIMEOUT,
            debug=False,
        )

        with patch("pagerangers.call_endpoint") as mock_call:
            mock_call.return_value = mock_keyword_response

            args = MagicMock()
            args.json = True
            args.keyword = "SEO tools"
            args.top = DEFAULT_TOP_URLS

            captured = StringIO()
            with patch("sys.stdout", captured):
                result = cmd_keyword(args, ctx)

            assert result == EXIT_SUCCESS
            output = json.loads(captured.getvalue())
            assert output["main_keyword"] == "SEO tools"
            assert output["search_volume"] == EXPECTED_SEARCH_VOLUME


class TestErrorHandling:
    """Tests for error handling."""

    def test_http_401_error(self) -> None:
        """Handle 401 authentication error."""
        with patch("pagerangers.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://test.com",
                code=HTTP_UNAUTHORIZED,
                msg="Unauthorized",
                hdrs={},
                fp=BytesIO(b"Unauthorized"),
            )

            with pytest.raises(RuntimeError, match="Authentication failed"):
                request_json("GET", "http://test.com", {}, None, DEFAULT_TIMEOUT)

    def test_http_429_rate_limit(self) -> None:
        """Handle 429 rate limit error."""
        with patch("pagerangers.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://test.com",
                code=HTTP_TOO_MANY_REQUESTS,
                msg="Too Many Requests",
                hdrs={},
                fp=BytesIO(b"Rate limited"),
            )

            with pytest.raises(RuntimeError, match="Rate limit exceeded"):
                request_json("GET", "http://test.com", {}, None, DEFAULT_TIMEOUT)
