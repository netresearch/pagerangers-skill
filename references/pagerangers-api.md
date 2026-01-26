# PageRangers API Reference

Complete API documentation for the PageRangers Monitoring endpoints.

## Base URL

```
https://api.pagerangers.com
```

## Authentication

All endpoints require:
- `projectHash`: Your project identifier
- `apiKey`: Your API key from Profile → API Settings

## Available Endpoints

### Keywords (`/Monitoring/Keywords/`)

Returns all keywords defined in the project.

**Cost:** 1 Credit

**Parameters:**
- `projectHash` (required)
- `apiKey` (required)
- `format` (optional): `json` or `xml`

### Rankings (`/Monitoring/Rankings/`)

Returns current ranking positions for all keywords.

**Cost:** 1 Credit

**Parameters:**
- `projectHash` (required)
- `apiKey` (required)
- `date` (optional): Unix timestamp
- `limit` (optional): Max 1000
- `offset` (optional): Skip results
- `tagfilter` (optional): Comma-separated tag list
- `competitorDomain` (optional): Compare with competitor
- `format` (optional): `json` or `xml`

### Ranking Changes (`/Monitoring/RankingChanges/`)

Shows how rankings changed between two dates.

**Cost:** 1 Credit

**Parameters:**
- `projectHash` (required)
- `apiKey` (required)
- `fromDate` (optional): Unix timestamp (default: 7 days ago)
- `toDate` (optional): Unix timestamp
- `typeFilter` (optional): `all`, `winner`, `looser`, `in`, `out`
- `limit`, `offset`, `tagfilter`, `format`

### Keyword SERP (`/Monitoring/KeywordSerp/`)

Returns SERP results for a specific keyword.

**Cost:** 1 Credit

**Parameters:**
- `projectHash` (required)
- `apiKey` (required)
- `keyword` (required): The keyword to analyze
- `date` (optional): Unix timestamp
- `format` (optional): `json` or `xml`

### Keyword Prospects (`/Monitoring/KeywordProspects/`)

Identifies keywords with best ranking opportunities.

**Cost:** 1 Credit

**Parameters:**
- `projectHash` (required)
- `apiKey` (required)
- `limit`, `offset`, `tagfilter`, `format`

### Main KPIs (`/Monitoring/MainKpis/`)

Returns project performance indicators.

**Cost:** 1 Credit

**Response includes:**
- Ranking Index
- Keywords in Top 10
- Keywords in Top 100
- Average position of ranking keywords

**Parameters:**
- `projectHash` (required)
- `apiKey` (required)
- `competitorDomain` (optional)
- `tagfilter`, `format`

### URL Switches (`/Monitoring/UrlSwitches/`)

Identifies potential URL changes for top rankings.

**Cost:** 1 Credit

### Multiple URL Rankings (`/Monitoring/MultipleUrlRankings/`)

Keywords ranking with multiple URLs in SERPs.

**Cost:** 1 Credit

### Competitors (`/Monitoring/Competitors/`)

Competitor data with ranking indices.

**Cost:** 2 Credits

### Competitor Rankings (`/Monitoring/CompetitorRankings/`)

Detailed competitor ranking positions.

**Cost:** 3 Credits

## Credential Setup

Create `~/.env.pagerangers`:

```bash
# PageRangers API Credentials
PAGERANGERS_API_TOKEN=your_api_key_here
PAGERANGERS_PROJECT_HASH=your_project_hash_here

# Optional overrides
# PAGERANGERS_BASE_URL=https://api.pagerangers.com
# PAGERANGERS_TIMEOUT=30
```

## Config File Structure

The `pagerangers-api.json` maps endpoints to response paths:

```json
{
  "base_url": "https://api.pagerangers.com",
  "endpoints": {
    "keyword": {
      "method": "GET",
      "path": "/Monitoring/KeywordSerp/",
      "query": {
        "keyword": "{keyword}",
        "projectHash": "{project_hash}",
        "apiKey": "{api_token}"
      },
      "response": {
        "main_keyword": "keyword",
        "search_volume": "searchVolume",
        "top_urls": "serp"
      }
    }
  }
}
```

### Placeholders

| Placeholder | Source |
|-------------|--------|
| `{keyword}` | Command argument |
| `{api_token}` | `PAGERANGERS_API_TOKEN` env |
| `{project_hash}` | `PAGERANGERS_PROJECT_HASH` env |

### Response Path Syntax

Use dot notation with optional array indexes:

```
data.keyword          → payload["data"]["keyword"]
serp[0].url           → payload["serp"][0]["url"]
results.items[2].name → payload["results"]["items"][2]["name"]
```

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 401 | Unauthorized | Check API token |
| 403 | Forbidden | Check project hash |
| 404 | Not found | Check endpoint path |
| 429 | Rate limited | Wait and retry |
| 500 | Server error | Contact PageRangers support |

## API Credits

| Endpoint | Cost |
|----------|------|
| Most endpoints | 1 credit |
| Competitors | 2 credits |
| CompetitorRankings | 3 credits |

SEO Suite plan includes 100 credits/month.

## External Documentation

- [PageRangers API Handbook](https://pagerangers.com/toolbox-handbuch/api-beta-1/)
- [Keyword Management](https://pagerangers.com/toolbox-handbuch/monitoring/handbuch-keyword-verwaltung/)
