# Error Handling

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 | Invalid API token | Check `PAGERANGERS_API_TOKEN` in `~/.env.pagerangers` |
| 403 | Invalid project | Check `PAGERANGERS_PROJECT_HASH` in `~/.env.pagerangers` |
| 429 | Rate limit exceeded | Wait and retry; SEO Suite includes 100 credits/month |
| Timeout | Slow network | Increase `PAGERANGERS_TIMEOUT` (default: 30s) |
| Empty keyword data | Keyword not in Explorer database | See `module-distinction.md`; use `rankings` for Monitoring keywords |

## Debugging

```bash
# Enable debug output to see raw API responses
python3 scripts/pagerangers.py --debug keyword "test"
```
