# PageRangers Module Distinction

PageRangers has two separate data sources that are **not interconnected**:

| Module | Description | Skill Commands |
|--------|-------------|----------------|
| **Monitoring** | Custom keywords you add to track your rankings | `kpis`, `rankings`, `prospects` |
| **Explorer** | PageRangers' general keyword database with SERP data | `keyword` |

## Key Point

Keywords in your Monitoring list are NOT automatically in the Explorer database. The `keyword` command queries Explorer data (search volume, competition, top URLs). If a keyword exists only in your Monitoring list, the `keyword` command returns empty data.

## What to Use When

- Use `rankings` to see positions for keywords you're tracking (Monitoring)
- Use `keyword` for SERP analysis of keywords in PageRangers Explorer database
- Not all keywords have Explorer data available
