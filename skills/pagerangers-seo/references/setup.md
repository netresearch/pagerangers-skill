# Setup and Authentication

## Getting Credentials

1. Log in to [PageRangers](https://www.pagerangers.com)
2. Go to **Profile → API Settings**
3. Copy your **API Token** and **Project Hash**
4. Store in `~/.env.pagerangers`

## Credentials File

```bash
cat > ~/.env.pagerangers << 'EOF'
PAGERANGERS_API_TOKEN=your_api_key_here
PAGERANGERS_PROJECT_HASH=your_project_hash_here
EOF
```

## Optional Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PAGERANGERS_API_TOKEN` | Yes | API key from PageRangers profile |
| `PAGERANGERS_PROJECT_HASH` | Yes | Project identifier |
| `PAGERANGERS_BASE_URL` | No | Override API URL |
| `PAGERANGERS_TIMEOUT` | No | Request timeout (default: 30s) |
