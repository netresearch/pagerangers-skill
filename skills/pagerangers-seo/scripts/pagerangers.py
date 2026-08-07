#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""PageRangers SEO API client for AI assistants.

Supports multiple commands:
  keyword   - Analyze a specific keyword (SERP data)
  rankings  - Get current keyword rankings
  kpis      - Get main KPIs (ranking index, top 10/100)
  prospects - Find high-opportunity keywords
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

# HTTP Status Codes
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_TOO_MANY_REQUESTS = 429

# Competition Thresholds
COMPETITION_LOW_THRESHOLD = 0.33
COMPETITION_MEDIUM_THRESHOLD = 0.66

# Default Values
DEFAULT_TIMEOUT = 30
DEFAULT_TOP_URLS = 5
DEFAULT_LIMIT = 20
MAX_RELATED_KEYWORDS = 10


@dataclass
class CommandContext:
    """Context for command execution."""

    config: dict
    variables: dict[str, str]
    timeout: int
    debug: bool


def load_env_file(path: Path) -> None:
    """Load environment variables from a file."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_config(path: Path) -> dict:
    """Load JSON configuration file."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def substitute(value: str | dict | list | None, variables: dict[str, str]) -> str | dict | list | None:
    """Replace {placeholder} strings with variable values."""
    if isinstance(value, str):
        result = value
        for key, val in variables.items():
            result = result.replace(f"{{{key}}}", val)
        return result
    if isinstance(value, dict):
        return {key: substitute(item, variables) for key, item in value.items()}
    if isinstance(value, list):
        return [substitute(item, variables) for item in value]
    return value


def get_by_path(data: dict | list | None, path: str) -> str | dict | list | None:
    """Extract value from nested dict using dot notation."""
    if not path:
        return data
    current = data
    for part in path.split("."):
        if part == "":
            continue
        if "[" in part and part.endswith("]"):
            name, idx_part = part[:-1].split("[", 1)
            if name:
                current = current.get(name) if isinstance(current, dict) else None
            if current is None:
                return None
            idx = int(idx_part)
            current = current[idx] if isinstance(current, list) and idx < len(current) else None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def normalize_urls(value: list | None, limit: int | None = None) -> list[str]:
    """Extract URLs from SERP results."""
    if not isinstance(value, list):
        return []
    urls = []
    for item in value:
        if isinstance(item, dict):
            url = item.get("url") or item.get("link") or item.get("href") or item.get("domain")
            if url:
                urls.append(url)
        elif isinstance(item, str):
            urls.append(item)
    if limit is not None:
        return urls[:limit]
    return urls


def normalize_competition(value: float | int | str | None) -> str:
    """Normalize competition score to low/medium/high."""
    if value is None:
        return "unknown"
    if isinstance(value, (int, float)):
        if value <= COMPETITION_LOW_THRESHOLD:
            return "low"
        if value <= COMPETITION_MEDIUM_THRESHOLD:
            return "medium"
        return "high"
    return str(value)


def request_json(method: str, url: str, headers: dict, body: dict | None, timeout: int) -> dict:
    """Make HTTP request and return JSON response."""
    data = None
    req_headers = {"Accept": "application/json", "User-Agent": "PageRangers-Skill/1.0"}
    req_headers.update(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=data, method=method, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code == HTTP_UNAUTHORIZED:
            raise RuntimeError("Authentication failed. Check PAGERANGERS_API_TOKEN.") from exc
        if exc.code == HTTP_FORBIDDEN:
            raise RuntimeError("Access denied. Check PAGERANGERS_PROJECT_HASH.") from exc
        if exc.code == HTTP_TOO_MANY_REQUESTS:
            raise RuntimeError("Rate limit exceeded. Try again later.") from exc
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Connection error: {exc.reason}") from exc

    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid JSON response from API") from exc


def call_endpoint(ctx: CommandContext, endpoint_name: str) -> dict:
    """Call a configured API endpoint."""
    base_url = os.environ.get("PAGERANGERS_BASE_URL", ctx.config.get("base_url", ""))
    if not base_url:
        raise RuntimeError("Missing base_url in config")

    endpoint = ctx.config.get("endpoints", {}).get(endpoint_name)
    if not endpoint:
        raise RuntimeError(f"Unknown endpoint: {endpoint_name}")

    endpoint = substitute(endpoint, ctx.variables)
    method = endpoint.get("method", "GET").upper()
    path = endpoint.get("path", "")

    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    query = endpoint.get("query")
    if query:
        url += "?" + urllib.parse.urlencode(query)

    if ctx.debug:
        safe_url = url.replace(ctx.variables.get("api_token", ""), "***")
        print(f"[DEBUG] {method} {safe_url}", file=sys.stderr)

    result = request_json(method, url, endpoint.get("headers", {}), endpoint.get("body"), ctx.timeout)

    if isinstance(result, dict) and "errormessage" in result:
        error_msg = result["errormessage"]
        if "api-key" in error_msg.lower():
            raise RuntimeError(f"API Error: {error_msg}. Your API key may not have access to this endpoint.")
        raise RuntimeError(f"API Error: {error_msg}")

    return result


def cmd_keyword(args: argparse.Namespace, ctx: CommandContext) -> int:
    """Analyze a specific keyword."""
    ctx.variables["keyword"] = args.keyword

    try:
        payload = call_endpoint(ctx, "keyword")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    response_map = ctx.config.get("endpoints", {}).get("keyword", {}).get("response", {})

    result = {
        "main_keyword": get_by_path(payload, response_map.get("main_keyword", "")) or args.keyword,
        "search_volume": get_by_path(payload, response_map.get("search_volume", "")) or "unknown",
        "competition": normalize_competition(get_by_path(payload, response_map.get("competition", ""))),
        "top_urls": normalize_urls(get_by_path(payload, response_map.get("top_urls", "")), args.top),
        "important_keywords": get_by_path(payload, response_map.get("important_keywords", "")) or [],
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print(f"Keyword: {result['main_keyword']}")
    print(f"Search Volume: {result['search_volume']}")
    print(f"Competition: {result['competition']}")
    if result["top_urls"]:
        print(f"\nTop {len(result['top_urls'])} URLs:")
        for i, url in enumerate(result["top_urls"], 1):
            print(f"  {i}. {url}")
    if result["important_keywords"]:
        print("\nRelated Keywords:")
        for kw in result["important_keywords"][:MAX_RELATED_KEYWORDS]:
            print(f"  - {kw}")
    return 0


def cmd_rankings(args: argparse.Namespace, ctx: CommandContext) -> int:
    """Get current keyword rankings."""
    try:
        payload = call_endpoint(ctx, "rankings")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    response_map = ctx.config.get("endpoints", {}).get("rankings", {}).get("response", {})
    keywords = get_by_path(payload, response_map.get("keywords", "")) or []

    if args.json:
        print(json.dumps({"rankings": keywords[: args.limit]}, indent=2, ensure_ascii=False))
        return 0

    print(f"Top {min(len(keywords), args.limit)} Keyword Rankings:\n")
    for i, kw in enumerate(keywords[: args.limit], 1):
        name = kw.get("keyword", kw.get("name", "unknown"))
        pos = kw.get("position", kw.get("rank", "?"))
        url = kw.get("url", kw.get("rankingUrl", ""))
        print(f"  {i}. [{pos}] {name}")
        if url:
            print(f"      {url}")
    return 0


def cmd_kpis(args: argparse.Namespace, ctx: CommandContext) -> int:
    """Get main KPIs."""
    try:
        payload = call_endpoint(ctx, "main_kpis")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    response_map = ctx.config.get("endpoints", {}).get("main_kpis", {}).get("response", {})

    result = {
        "ranking_index": get_by_path(payload, response_map.get("ranking_index", "")),
        "top_10_count": get_by_path(payload, response_map.get("top_10_count", "")),
        "top_100_count": get_by_path(payload, response_map.get("top_100_count", "")),
        "average_position": get_by_path(payload, response_map.get("average_position", "")),
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print("Project KPIs:\n")
    print(f"  Ranking Index:     {result['ranking_index'] or 'N/A'}")
    print(f"  Keywords in Top 10:  {result['top_10_count'] or 'N/A'}")
    print(f"  Keywords in Top 100: {result['top_100_count'] or 'N/A'}")
    print(f"  Average Position:    {result['average_position'] or 'N/A'}")
    return 0


def cmd_prospects(args: argparse.Namespace, ctx: CommandContext) -> int:
    """Find high-opportunity keywords."""
    try:
        payload = call_endpoint(ctx, "prospects")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    response_map = ctx.config.get("endpoints", {}).get("prospects", {}).get("response", {})
    prospects = get_by_path(payload, response_map.get("prospects", "")) or []

    if args.json:
        print(json.dumps({"prospects": prospects[: args.limit]}, indent=2, ensure_ascii=False))
        return 0

    print(f"Top {min(len(prospects), args.limit)} Keyword Opportunities:\n")
    for i, kw in enumerate(prospects[: args.limit], 1):
        name = kw.get("keyword", kw.get("name", "unknown"))
        pos = kw.get("position", kw.get("rank", "?"))
        volume = kw.get("searchVolume", kw.get("volume", "?"))
        print(f"  {i}. {name}")
        print(f"      Position: {pos}, Search Volume: {volume}")
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="PageRangers SEO API client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  keyword <kw>   Analyze a specific keyword (SERP, volume, competition)
  rankings       Get current keyword rankings for the project
  kpis           Get main KPIs (ranking index, top 10/100 counts)
  prospects      Find high-opportunity keywords

Environment Variables:
  PAGERANGERS_API_TOKEN     Your PageRangers API key (required)
  PAGERANGERS_PROJECT_HASH  Your project identifier (required)
  PAGERANGERS_BASE_URL      Override API base URL (optional)
  PAGERANGERS_TIMEOUT       Request timeout in seconds (default: 30)

Configuration:
  Store credentials in ~/.env.pagerangers:
    PAGERANGERS_API_TOKEN=your_api_key
    PAGERANGERS_PROJECT_HASH=your_project_hash
""",
    )

    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--debug", action="store_true", help="Show debug info")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parent.parent / "references" / "pagerangers-api.json"),
        help="Path to API config JSON",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    kw_parser = subparsers.add_parser("keyword", help="Analyze a keyword")
    kw_parser.add_argument("keyword", help="Keyword to analyze")
    kw_parser.add_argument("--top", type=int, default=DEFAULT_TOP_URLS, help=f"Top URLs (default: {DEFAULT_TOP_URLS})")

    rank_parser = subparsers.add_parser("rankings", help="Get keyword rankings")
    rank_parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"Max results (default: {DEFAULT_LIMIT})")

    subparsers.add_parser("kpis", help="Get main KPIs")

    prosp_parser = subparsers.add_parser("prospects", help="Find keyword opportunities")
    prosp_parser.add_argument(
        "--limit", type=int, default=DEFAULT_LIMIT, help=f"Max results (default: {DEFAULT_LIMIT})"
    )

    return parser


def get_command_handlers() -> dict[str, Callable[[argparse.Namespace, CommandContext], int]]:
    """Return mapping of command names to handler functions."""
    return {
        "keyword": cmd_keyword,
        "rankings": cmd_rankings,
        "kpis": cmd_kpis,
        "prospects": cmd_prospects,
    }


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    load_env_file(Path.home() / ".env.pagerangers")

    config_path = Path(args.config)
    if not config_path.is_file():
        print(f"Error: Config not found: {config_path}", file=sys.stderr)
        print("Run from skill directory or specify --config path", file=sys.stderr)
        return 1

    config = load_config(config_path)

    token = os.environ.get("PAGERANGERS_API_TOKEN")
    project_hash = os.environ.get("PAGERANGERS_PROJECT_HASH")
    if not token or not project_hash:
        print("Error: Missing credentials.", file=sys.stderr)
        print("\nSet environment variables or create ~/.env.pagerangers with:", file=sys.stderr)
        print("  PAGERANGERS_API_TOKEN=your_api_key", file=sys.stderr)
        print("  PAGERANGERS_PROJECT_HASH=your_project_hash", file=sys.stderr)
        return 1

    ctx = CommandContext(
        config=config,
        variables={"api_token": token, "project_hash": project_hash},
        timeout=int(os.environ.get("PAGERANGERS_TIMEOUT", str(DEFAULT_TIMEOUT))),
        debug=args.debug,
    )

    handlers = get_command_handlers()
    handler = handlers.get(args.command)
    if handler:
        return handler(args, ctx)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
