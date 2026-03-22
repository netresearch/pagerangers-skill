# Architecture

## Purpose

This repository is an AI agent skill that provides a CLI tool and procedural knowledge for querying the PageRangers Monitoring API. Unlike content-only skills, this repo includes executable Python code and a test suite.

## Component Overview

### Skill Definition

- **SKILL.md**: Entry point loaded by AI agents. Contains command descriptions, usage examples, and reference links.
- **AGENTS.md**: Agent-facing instructions with activation triggers, workflow, error handling, and module distinction (Monitoring vs Explorer).

### CLI Tool (`scripts/`)

- **pagerangers.py**: Main CLI implementation. Provides subcommands (`kpis`, `rankings`, `keyword`, `prospects`) for querying the PageRangers API. Supports `--json` output for structured data parsing by agents.
- **detect_credentials.py**: Helper for credential detection and validation.

### References (`references/`)

API documentation and endpoint configuration:
- **pagerangers-api.md**: Human-readable API documentation
- **pagerangers-api.json**: Machine-readable endpoint configuration

### Tests (`tests/`)

Pytest-based test suite with response mocking:
- **conftest.py**: Shared fixtures and mock configurations
- **test_pagerangers.py**: Tests for the CLI tool

### Configuration

- **pyproject.toml**: Python project config (dependencies, ruff linting, pytest, coverage settings)
- **uv.lock**: Locked dependencies for reproducible installs

## Data Flow

1. Agent loads `SKILL.md` when SEO/PageRangers intent is detected
2. Agent checks for credentials in `~/.env.pagerangers`
3. Agent runs `python3 scripts/pagerangers.py --json <subcommand>` to query the API
4. Agent interprets JSON output and presents insights to the user

## Key Design Decisions

- **Standalone CLI**: The script runs independently with no framework dependencies -- just Python 3.10+ and stdlib.
- **Credential isolation**: Credentials stored in `~/.env.pagerangers`, not in project files.
- **JSON-first output**: `--json` flag enables structured output for reliable agent parsing.
- **Module distinction**: Monitoring (tracked keywords) and Explorer (general SERP database) are separate API domains with different data availability.
