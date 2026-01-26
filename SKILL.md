---
name: pagerangers-seo
description: "PageRangers SEO API integration for AI assistants. TRIGGER when user mentions PageRangers, SEO keywords, search rankings, SERP analysis, or keyword research. Provides keyword analysis, ranking data, KPIs, and keyword opportunities via the PageRangers Monitoring API. Requires python3. Works with Claude Code and Codex CLI."
license: MIT
metadata:
  author: netresearch
  version: "1.0.0"
  repository: https://github.com/netresearch/pagerangers-skill
  compatibility: "python3, Claude Code, Codex CLI"
---

# PageRangers SEO

Query the PageRangers Monitoring API for SEO insights directly from your AI assistant.

## Commands

| Command | Description |
|---------|-------------|
| `keyword <term>` | Analyze a keyword (SERP, volume, competition) |
| `rankings` | List current keyword rankings |
| `kpis` | Get project KPIs (ranking index, top 10/100) |
| `prospects` | Find high-opportunity keywords |

## Quick Start

```bash
# 1. Create credentials file
cat > ~/.env.pagerangers << 'EOF'
PAGERANGERS_API_TOKEN=your_api_key_here
PAGERANGERS_PROJECT_HASH=your_project_hash_here
EOF

# 2. Run commands
python3 scripts/pagerangers.py keyword "SEO Analyse" --top 5
python3 scripts/pagerangers.py rankings --limit 10
python3 scripts/pagerangers.py kpis
python3 scripts/pagerangers.py prospects --limit 10
```

## Usage Examples

### Keyword Analysis
```bash
python3 scripts/pagerangers.py keyword "online marketing" --top 10 --json
```
Returns: keyword, search volume, competition (low/medium/high), top URLs, related keywords.

### Project Rankings
```bash
python3 scripts/pagerangers.py rankings --limit 20
```
Returns: keyword, position, ranking URL.

### Project KPIs
```bash
python3 scripts/pagerangers.py kpis --json
```
Returns: ranking index, top 10 count, top 100 count, average position.

### Keyword Opportunities
```bash
python3 scripts/pagerangers.py prospects --limit 10
```
Returns: keywords with best ranking potential.

## AI Workflow

When asked to analyze SEO data:

1. **Check credentials**: Verify `~/.env.pagerangers` exists
2. **Run appropriate command**: Match user intent to command
3. **Summarize results**: Present data in clear format
4. **Provide insights**: Interpret the data for actionable recommendations

### Example Interaction
```
User: "What's the search volume for 'SEO tools'?"

AI: [Runs: python3 scripts/pagerangers.py keyword "SEO tools" --json]

    Keyword: SEO tools
    Search Volume: 12,100
    Competition: high

    Top 5 URLs:
    1. https://example.com/best-seo-tools
    2. https://another.com/seo-software
    ...
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PAGERANGERS_API_TOKEN` | Yes | API key from PageRangers profile |
| `PAGERANGERS_PROJECT_HASH` | Yes | Project identifier |
| `PAGERANGERS_BASE_URL` | No | Override API URL |
| `PAGERANGERS_TIMEOUT` | No | Request timeout (default: 30s) |

### Getting Credentials

1. Log in to PageRangers
2. Go to Profile → API Settings
3. Copy API Token and Project Hash
4. Store in `~/.env.pagerangers`

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 | Invalid API token | Check `PAGERANGERS_API_TOKEN` |
| 403 | Invalid project | Check `PAGERANGERS_PROJECT_HASH` |
| 429 | Rate limit | Wait and retry |
| Timeout | Slow network | Increase `PAGERANGERS_TIMEOUT` |
| Empty keyword data | Keyword not in Explorer | See "Module Distinction" below |

## PageRangers Module Distinction

PageRangers has two separate data sources that are **not interconnected**:

| Module | Description | Skill Commands |
|--------|-------------|----------------|
| **Monitoring** | Custom keywords you add to track your rankings | `kpis`, `rankings`, `prospects` |
| **Explorer** | PageRangers' general keyword database with SERP data | `keyword` |

**Important:** Keywords in your Monitoring list are NOT automatically in the Explorer database. The `keyword` command queries Explorer data (search volume, competition, top URLs). If a keyword exists only in your Monitoring list, the `keyword` command returns empty data.

**What to use when:**
- Use `rankings` to see positions for keywords you're tracking (Monitoring)
- Use `keyword` for SERP analysis of keywords in PageRangers Explorer database
- Not all keywords have Explorer data available

## API Costs

Each API call costs 1 credit (except Competitors: 2, CompetitorRankings: 3).
SEO Suite includes 100 credits/month.

## Resources

- `scripts/pagerangers.py` - Main CLI client
- `references/pagerangers-api.md` - Detailed API documentation
- `references/pagerangers-api.json` - Endpoint configuration
