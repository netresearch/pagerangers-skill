"""Tests for PageRangers credential detection hook."""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from detect_credentials import (
    check_credentials,
    contains_pagerangers_keywords,
    main,
    parse_prompt,
)


class TestKeywordDetection:
    """Tests for PageRangers keyword detection."""

    def test_pagerangers_keyword_detected(self) -> None:
        """Direct 'pagerangers' mention triggers detection."""
        assert contains_pagerangers_keywords("Check my PageRangers data")
        assert contains_pagerangers_keywords("pagerangers rankings")
        assert contains_pagerangers_keywords("PAGERANGERS api")

    def test_skill_commands_with_seo_context(self) -> None:
        """Skill command names with SEO context trigger detection."""
        assert contains_pagerangers_keywords("show me seo rankings")
        assert contains_pagerangers_keywords("get SEO kpis for the site")
        assert contains_pagerangers_keywords("find seo prospects")

    def test_ranking_index_keyword(self) -> None:
        """PageRangers-specific 'ranking index' triggers detection."""
        assert contains_pagerangers_keywords("what is my ranking index")
        assert contains_pagerangers_keywords("check the ranking index")

    def test_generic_seo_no_trigger(self) -> None:
        """Generic SEO mentions without specific keywords don't trigger."""
        assert not contains_pagerangers_keywords("improve my SEO")
        assert not contains_pagerangers_keywords("SEO best practices")
        assert not contains_pagerangers_keywords("search engine optimization")

    def test_unrelated_queries_no_trigger(self) -> None:
        """Unrelated queries don't trigger detection."""
        assert not contains_pagerangers_keywords("write a Python function")
        assert not contains_pagerangers_keywords("fix the bug in auth.py")
        assert not contains_pagerangers_keywords("what is the weather")

    def test_empty_and_none(self) -> None:
        """Empty or None input returns False."""
        assert not contains_pagerangers_keywords("")
        assert not contains_pagerangers_keywords(None)


class TestPromptParsing:
    """Tests for stdin prompt parsing."""

    def test_json_with_prompt_field(self) -> None:
        """Parse JSON input with 'prompt' field."""
        data = json.dumps({"prompt": "check pagerangers"})
        assert parse_prompt(data) == "check pagerangers"

    def test_json_with_message_field(self) -> None:
        """Parse JSON input with 'message' field."""
        data = json.dumps({"message": "seo rankings please"})
        assert parse_prompt(data) == "seo rankings please"

    def test_json_with_content_field(self) -> None:
        """Parse JSON input with 'content' field."""
        data = json.dumps({"content": "show kpis"})
        assert parse_prompt(data) == "show kpis"

    def test_plain_text_fallback(self) -> None:
        """Plain text input returned as-is."""
        assert parse_prompt("plain text query") == "plain text query"

    def test_empty_input(self) -> None:
        """Empty input returns empty string."""
        assert parse_prompt("") == ""
        assert parse_prompt(None) == ""


class TestCredentialCheck:
    """Tests for credential file checking."""

    def test_credentials_file_missing(self, tmp_path: Path) -> None:
        """Missing credentials file returns error info."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()

        with patch("detect_credentials.Path.home", return_value=fake_home):
            result = check_credentials()

        assert result["valid"] is False
        assert "not found" in result["message"].lower()

    def test_credentials_file_empty(self, tmp_path: Path) -> None:
        """Empty credentials file returns error info."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        creds_file = fake_home / ".env.pagerangers"
        creds_file.write_text("")

        with patch("detect_credentials.Path.home", return_value=fake_home):
            result = check_credentials()

        assert result["valid"] is False
        assert "missing" in result["message"].lower()

    def test_credentials_missing_token(self, tmp_path: Path) -> None:
        """Credentials without API token returns error."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        creds_file = fake_home / ".env.pagerangers"
        creds_file.write_text("PAGERANGERS_PROJECT_HASH=ABC123\n")

        with patch("detect_credentials.Path.home", return_value=fake_home):
            result = check_credentials()

        assert result["valid"] is False
        assert "token" in result["message"].lower()

    def test_credentials_missing_hash(self, tmp_path: Path) -> None:
        """Credentials without project hash returns error."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        creds_file = fake_home / ".env.pagerangers"
        creds_file.write_text("PAGERANGERS_API_TOKEN=secret123\n")

        with patch("detect_credentials.Path.home", return_value=fake_home):
            result = check_credentials()

        assert result["valid"] is False
        assert "hash" in result["message"].lower()

    def test_credentials_valid(self, tmp_path: Path) -> None:
        """Valid credentials file returns success."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        creds_file = fake_home / ".env.pagerangers"
        creds_file.write_text("PAGERANGERS_API_TOKEN=secret123\nPAGERANGERS_PROJECT_HASH=ABC123\n")

        with patch("detect_credentials.Path.home", return_value=fake_home):
            result = check_credentials()

        assert result["valid"] is True


class TestMainFunction:
    """Integration tests for main hook function."""

    def test_no_keywords_no_output(self, capsys: pytest.CaptureFixture) -> None:
        """No PageRangers keywords produces no output."""
        stdin_data = json.dumps({"prompt": "write a function"})

        with patch("sys.stdin", StringIO(stdin_data)):
            main()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_keywords_with_valid_creds_no_output(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """PageRangers keywords with valid credentials produces no output."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        creds_file = fake_home / ".env.pagerangers"
        creds_file.write_text("PAGERANGERS_API_TOKEN=secret\nPAGERANGERS_PROJECT_HASH=ABC\n")

        stdin_data = json.dumps({"prompt": "check pagerangers rankings"})

        with patch("sys.stdin", StringIO(stdin_data)), patch("detect_credentials.Path.home", return_value=fake_home):
            main()

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_keywords_with_missing_creds_outputs_help(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """PageRangers keywords with missing credentials outputs setup help."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        # No credentials file created

        stdin_data = json.dumps({"prompt": "show my pagerangers kpis"})

        with patch("sys.stdin", StringIO(stdin_data)), patch("detect_credentials.Path.home", return_value=fake_home):
            main()

        captured = capsys.readouterr()
        assert "<user-prompt-submit-hook>" in captured.out
        assert "PAGERANGERS_API_TOKEN" in captured.out
        assert "PAGERANGERS_PROJECT_HASH" in captured.out
        assert ".env.pagerangers" in captured.out
