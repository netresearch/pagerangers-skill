# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-01-26

### Added

- Initial release of PageRangers SEO skill
- `kpis` command for project KPIs (ranking index, top 10/100 counts, average position)
- `rankings` command for current keyword positions
- `keyword` command for SERP analysis (search volume, competition, top URLs)
- `prospects` command for high-opportunity keyword identification
- Comprehensive test suite with 34 tests
- Ruff linting with zero ignores
- GitHub Actions CI workflow with Python 3.12/3.13
- Renovate configuration for automated dependency updates
- UserPromptSubmit hook for credential detection and setup guidance

### Technical

- Uses `CommandContext` dataclass for clean parameter passing
- Named constants for all magic values (HTTP codes, thresholds, defaults)
- Full type hints throughout codebase
- Inline script dependencies for `uv run --script` compatibility

[Unreleased]: https://github.com/netresearch/pagerangers-skill/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/netresearch/pagerangers-skill/releases/tag/v1.0.0
