#!/usr/bin/env python3
"""
UserPromptSubmit hook to detect PageRangers-related queries and check credentials.
Provides setup instructions if credentials are missing.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Keywords that indicate PageRangers-specific queries
PAGERANGERS_PATTERNS = [
    r"\bpagerangers\b",  # Direct mention
    r"\branking\s+index\b",  # PageRangers-specific metric
]

# SEO + skill command combinations
SEO_COMMAND_PATTERN = r"\bseo\b.*\b(rankings?|kpis?|prospects?)\b|\b(rankings?|kpis?|prospects?)\b.*\bseo\b"

CREDENTIALS_FILE = ".env.pagerangers"
REQUIRED_VARS = ["PAGERANGERS_API_TOKEN", "PAGERANGERS_PROJECT_HASH"]


def contains_pagerangers_keywords(text: str | None) -> bool:
    """Check if text contains PageRangers-specific keywords."""
    if not text:
        return False

    text_lower = text.lower()

    # Check direct PageRangers patterns
    for pattern in PAGERANGERS_PATTERNS:
        if re.search(pattern, text_lower):
            return True

    # Check SEO + command keyword combinations
    return bool(re.search(SEO_COMMAND_PATTERN, text_lower))


def parse_prompt(input_data: str | None) -> str:
    """Parse prompt from stdin input (JSON or plain text)."""
    if not input_data:
        return ""

    # Try JSON parsing
    try:
        data = json.loads(input_data)
        return data.get("prompt", "") or data.get("message", "") or data.get("content", "") or ""
    except (json.JSONDecodeError, TypeError):
        return input_data


def check_credentials() -> dict[str, bool | str]:
    """Check if PageRangers credentials file exists and is valid."""
    creds_path = Path.home() / CREDENTIALS_FILE

    if not creds_path.exists():
        return {
            "valid": False,
            "message": f"Credentials file not found: ~/{CREDENTIALS_FILE}",
        }

    content = creds_path.read_text()

    missing_vars = []
    for var in REQUIRED_VARS:
        if var not in content or f"{var}=" not in content:
            missing_vars.append(var)

    if missing_vars:
        missing_str = ", ".join(missing_vars)
        return {
            "valid": False,
            "message": f"Missing required variables: {missing_str}",
        }

    # Check for empty values
    for var in REQUIRED_VARS:
        pattern = rf"{var}=\s*$"
        if re.search(pattern, content, re.MULTILINE):
            return {
                "valid": False,
                "message": f"Empty value for {var}",
            }

    return {"valid": True, "message": "Credentials valid"}


def output_setup_instructions(error_message: str) -> None:
    """Print setup instructions for missing credentials."""
    print(f"""<user-prompt-submit-hook>
PageRangers credentials issue: {error_message}

Create ~/.env.pagerangers with:

    PAGERANGERS_API_TOKEN=your_api_key
    PAGERANGERS_PROJECT_HASH=your_project_hash

Get credentials from PageRangers → Profile → API Settings
</user-prompt-submit-hook>""")


def main() -> None:
    """Main hook entry point."""
    try:
        input_data = sys.stdin.read()
    except Exception:
        return

    prompt = parse_prompt(input_data)

    if not contains_pagerangers_keywords(prompt):
        return

    result = check_credentials()

    if not result["valid"]:
        output_setup_instructions(result["message"])


if __name__ == "__main__":
    main()
