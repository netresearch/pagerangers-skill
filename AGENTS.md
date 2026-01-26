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
| `kpis` | Get project performance metrics | `python3 scripts/pagerangers.py kpis` |
| `rankings` | List keyword positions | `python3 scripts/pagerangers.py rankings --limit 20` |
| `keyword` | Analyze specific keyword | `python3 scripts/pagerangers.py keyword "SEO tools"` |
| `prospects` | Find opportunities | `python3 scripts/pagerangers.py prospects --limit 10` |

## Workflow

1. **Check credentials**: Verify `~/.env.pagerangers` exists with API token and project hash
2. **Select command**: Match user intent to appropriate command
3. **Execute**: Run command with appropriate flags (`--json` for structured output)
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
| Empty data | SERP not tracked | Enable SERP monitoring in PageRangers |

## Best Practices

1. Always use `--json` flag for structured data parsing
2. Limit results appropriately (`--limit 10-20` for readability)
3. Combine multiple data sources for comprehensive analysis
4. Interpret metrics in context of user's business goals

## Related Files

- `SKILL.md` - Main skill definition
- `scripts/pagerangers.py` - CLI implementation
- `references/pagerangers-api.md` - API documentation
- `references/pagerangers-api.json` - Endpoint configuration
