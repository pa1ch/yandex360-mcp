# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Release workflow (`.github/workflows/release.yml`): pushing a `vX.Y.Z` tag builds,
  runs tests, and then, in parallel, publishes to **PyPI** via Trusted Publishing (OIDC,
  no token), creates a **GitHub Release**, and publishes to the **MCP Registry** via
  GitHub OIDC. The tag must match the version in `pyproject.toml`; the `server.json`
  version is set from the tag automatically at publish time.
- This changelog.

## [0.1.1] - 2026-07-19

### Added
- MCP Registry manifest (`server.json`) and `mcp-name` marker for
  `io.github.pa1ch/yandex360-mcp`; published to the official MCP Registry.
- README section "Loading only the modules you need" and an MCP Registry badge.

## [0.1.0] - 2026-07-19

### Added
- Initial release: modular Yandex 360 MCP server with the `wiki` module (9 tools).
- stdio transport, install via `uvx`; published to PyPI; CI on Python 3.10–3.13.
