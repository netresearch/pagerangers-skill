# PageRangers SEO Skill - Agent Instructions

This file provides guidance for AI agents working with the PageRangers SEO skill.

## Overview

This skill provides access to the PageRangers Monitoring API for SEO data analysis. It enables AI assistants to retrieve keyword rankings, search volume data, competition metrics, and project KPIs.

## Activation Triggers

**AUTOMATICALLY ACTIVATE** when user mentions:

- PageRangers, SEO keywords, search rankings
- SERP analysis, keyword research
- Ranking positions, search volume
- SEO KPIs, monitoring data

## Available Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `kpis` | Get project performance metrics | `python3 skills/pagerangers-seo/scripts/pagerangers.py --json kpis` |
| `rankings` | List keyword positions | `python3 skills/pagerangers-seo/scripts/pagerangers.py --json rankings --limit 20` |
| `keyword` | Analyze specific keyword | `python3 skills/pagerangers-seo/scripts/pagerangers.py --json keyword "SEO tools"` |
| `prospects` | Find opportunities | `python3 skills/pagerangers-seo/scripts/pagerangers.py --json prospects --limit 10` |

> **Flag order:** Global flags (`--json`, `--debug`) must come **before** the subcommand.

## Workflow

1. **Check credentials**: Verify `~/.env.pagerangers` exists with API token and project hash
2. **Select command**: Match user intent to appropriate command
3. **Execute**: Run with `--json` flag **before** subcommand for structured output
4. **Interpret**: Present data with actionable insights

## Authentication Setup

If credentials are missing, guide user to create `~/.env.pagerangers`:

```bash
cat > ~/.env.pagerangers << 'EOF'
PAGERANGERS_API_TOKEN=your_api_key_here
PAGERANGERS_PROJECT_HASH=your_project_hash_here
EOF
```

Credentials are obtained from PageRangers → Profile → API Settings.

## Error Handling

| Error | Meaning | Solution |
|-------|---------|----------|
| 401 | Invalid token | Verify `PAGERANGERS_API_TOKEN` |
| 403 | Invalid project | Verify `PAGERANGERS_PROJECT_HASH` |
| 429 | Rate limited | Wait and retry |
| Empty keyword data | Keyword not in Explorer | Use `rankings` for Monitoring keywords; `keyword` requires Explorer data |

## Module Distinction

PageRangers Monitoring ≠ Explorer:

- **Monitoring** (kpis, rankings, prospects): Your tracked keywords
- **Explorer** (keyword command): PageRangers' general SERP database

Keywords in Monitoring don't automatically have Explorer data. If `keyword` returns empty, use `rankings` instead.

## Related Files

- `skills/pagerangers-seo/SKILL.md` - Main skill definition
- `skills/pagerangers-seo/scripts/pagerangers.py` - CLI implementation
- `skills/pagerangers-seo/references/pagerangers-api.md` - API documentation
- `skills/pagerangers-seo/references/pagerangers-api.json` - Endpoint configuration
