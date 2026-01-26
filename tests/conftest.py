"""Pytest fixtures for PageRangers API testing."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def mock_env() -> Generator[dict[str, str], None, None]:
    """Provide mock environment variables for testing."""
    env_vars = {
        "PAGERANGERS_API_TOKEN": "test-api-token-12345",
        "PAGERANGERS_PROJECT_HASH": "ABC1234",
        "PAGERANGERS_BASE_URL": "https://api.pagerangers.com",
        "PAGERANGERS_TIMEOUT": "30",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def config_path() -> Path:
    """Return path to the API config file."""
    return Path(__file__).parent.parent / "references" / "pagerangers-api.json"


@pytest.fixture
def api_config(config_path: Path) -> dict:
    """Load and return the API configuration."""
    with config_path.open() as f:
        return json.load(f)


@pytest.fixture
def mock_kpis_response() -> dict:
    """Sample KPIs API response."""
    return {
        "rankingindex": 7.4543557,
        "numberOfKeywordsInTop10": 13,
        "numberOfKeywordsTop100": 14,
        "averageTopPosition": 10.857142,
    }


@pytest.fixture
def mock_rankings_response() -> dict:
    """Sample rankings API response."""
    return {
        "rankings": [
            {
                "keyword": "typo3 agentur leipzig",
                "position": 5,
                "url": "https://example.com/typo3",
                "device": "Desktop",
                "searchengine": "Google - Germany",
            },
            {
                "keyword": "magento extensions",
                "position": 12,
                "url": "https://example.com/magento",
                "device": "Desktop",
                "searchengine": "Google - Germany",
            },
        ],
        "total": 2,
    }


@pytest.fixture
def mock_prospects_response() -> dict:
    """Sample prospects API response."""
    return {
        "prospects": [
            {
                "keyword": "typo3 update",
                "position": 91,
                "searchVolume": 1200,
            },
            {
                "keyword": "magento hosting",
                "position": 45,
                "searchVolume": 800,
            },
        ]
    }


@pytest.fixture
def mock_keyword_response() -> dict:
    """Sample keyword SERP API response."""
    return {
        "keyword": "SEO tools",
        "searchVolume": 12100,
        "competition": 0.75,
        "serp": [
            {"url": "https://example.com/seo-tools", "position": 1},
            {"url": "https://another.com/tools", "position": 2},
        ],
        "relatedKeywords": ["seo software", "seo checker", "seo analyzer"],
    }


@pytest.fixture
def mock_error_response() -> dict:
    """Sample API error response."""
    return {"errormessage": "Invalid api-key"}
