# PageRangers SEO Skill

[![License](https://img.shields.io/badge/License-MIT%20%2B%20CC--BY--SA--4.0-blue.svg)](#license)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

AI agent skill for querying the PageRangers Monitoring API. Works with Claude Code, Codex CLI, and other AI assistants supporting the Agent Skills specification.

## Features

- **Keyword Analysis**: SERP data, search volume, competition levels
- **Rankings**: Current keyword positions and ranking URLs
- **KPIs**: Ranking index, top 10/100 counts, average position
- **Prospects**: High-opportunity keyword identification

## Quick Start

```bash
# 1. Create credentials file
cat > ~/.env.pagerangers << 'EOF'
PAGERANGERS_API_TOKEN=your_api_key_here
PAGERANGERS_PROJECT_HASH=your_project_hash_here
EOF

# 2. Run commands (--json flag must come before subcommand)
python3 scripts/pagerangers.py --json kpis
python3 scripts/pagerangers.py --json rankings --limit 10
python3 scripts/pagerangers.py --json keyword "SEO tools" --top 5
python3 scripts/pagerangers.py --json prospects --limit 10
```

## Installation

### Marketplace (Recommended)

Add the [Netresearch marketplace](https://github.com/netresearch/claude-code-marketplace) once, then browse and install skills:

```bash
# Claude Code
/plugin marketplace add netresearch/claude-code-marketplace
```

### npx ([skills.sh](https://skills.sh))

Install with any [Agent Skills](https://agentskills.io)-compatible agent:

```bash
npx skills add https://github.com/netresearch/pagerangers-skill --skill pagerangers-seo
```

### Download Release

Download the [latest release](https://github.com/netresearch/pagerangers-skill/releases/latest) and extract to your agent's skills directory.

### Git Clone

```bash
git clone https://github.com/netresearch/pagerangers-skill.git
```

### Composer (PHP Projects)

```bash
composer require netresearch/pagerangers-skill
```

Requires [netresearch/composer-agent-skill-plugin](https://github.com/netresearch/composer-agent-skill-plugin).

## Development

### Setup

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=scripts --cov-report=html

# Lint code
ruff check scripts tests

# Format code
ruff format scripts tests
```

### Project Structure

```text
pagerangers-seo/
├── .claude-plugin/     # Claude Code plugin manifest
│   └── plugin.json
├── scripts/            # CLI scripts
│   └── pagerangers.py
├── references/         # API documentation
│   ├── pagerangers-api.json
│   └── pagerangers-api.md
├── tests/              # Pytest test suite
│   ├── conftest.py
│   └── test_pagerangers.py
├── SKILL.md            # Skill definition
├── AGENTS.md           # Agent documentation
├── pyproject.toml      # Python project config
└── README.md           # This file
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

## API Reference

See [references/pagerangers-api.md](references/pagerangers-api.md) for complete API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass: `pytest`
5. Ensure code is formatted: `ruff format`
6. Submit a pull request

## License

This project uses split licensing:

- **Code** (scripts, workflows, configs): [MIT](LICENSE-MIT)
- **Content** (skill definitions, documentation, references): [CC-BY-SA-4.0](LICENSE-CC-BY-SA-4.0)

See the individual license files for full terms.

## Author

[Netresearch DTT GmbH](https://www.netresearch.de/)
