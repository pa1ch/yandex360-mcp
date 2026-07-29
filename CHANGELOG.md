# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-07-29

### Fixed
- Пин зависимости на `mcp>=1.2.0,<2`. В MCP SDK 2.0.0 удалён модуль `mcp.server.fastmcp`
  (переехал в `mcp.server.mcpserver`), из-за чего `uvx yandex360-mcp` тянул 2.0.0 и сервер
  падал на импорте до старта — MCP-клиенты молча выкидывали его из списка серверов.

## [0.1.2] - 2026-07-19

### Added
- One-click **Claude Desktop** install: a `.mcpb` bundle (`manifest.json` + `.mcpbignore`)
  is built and attached to every GitHub Release. Users fill token fields in a form instead
  of editing JSON (requires `uv` installed on the machine).
- Release workflow (`.github/workflows/release.yml`): pushing a `vX.Y.Z` tag builds, runs
  tests, and in parallel publishes to **PyPI** (Trusted Publishing / OIDC, no token),
  builds the **.mcpb** bundle, creates a **GitHub Release**, and publishes to the
  **MCP Registry** (GitHub OIDC). The tag must match `pyproject.toml`; the `server.json`
  and `manifest.json` versions are set from the tag automatically at publish time.
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
