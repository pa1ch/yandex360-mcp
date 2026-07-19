# Yandex 360 MCP Server

[![PyPI version](https://img.shields.io/pypi/v/yandex360-mcp.svg)](https://pypi.org/project/yandex360-mcp/)
[![Tests](https://github.com/pa1ch/yandex360-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/pa1ch/yandex360-mcp/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

MCP server that gives AI assistants (Claude Code, Claude Desktop, Cursor, VS Code and
any other MCP client) tools to work with **[Yandex 360](https://360.yandex.com/)**
organization services — starting with **Yandex Wiki**. Transport is **stdio**, the only
runtime dependency is `mcp`, and it installs & runs through `uvx` without cloning.

🇷🇺 Документация на русском — [README_ru.md](README_ru.md).

> **Scope:** this server covers **Yandex 360** services (Wiki, and next Directory, Disk).
> **Yandex Tracker is intentionally out of scope** — it already has an excellent, mature
> server: **[aikts/yandex-tracker-mcp](https://github.com/aikts/yandex-tracker-mcp)**.
> Use the two side by side.

## Features

- 📖 **Yandex Wiki** — read and edit pages (YFM), full-text search, page tree navigation, create / update / append / delete.
- 🧩 **Modular by service** — each Yandex 360 service is a separate module. A module registers its tools **only if its tokens are set**, so the model is never handed tools for services you don't use — the context stays lean.
- 🔌 **Zero-friction install** — one dependency, stdio transport, runs via `uvx` straight from GitHub or PyPI.
- 🔐 **No secrets in code or config** — all tokens come from environment variables.

### Modules

| Module      | Status      | Description                                   |
|-------------|-------------|-----------------------------------------------|
| `wiki`      | ✅ available | Read/edit Yandex Wiki pages (YFM)             |
| `directory` | 🔜 planned  | Users and org structure (Yandex 360 Directory)|
| `disk`      | 🔜 planned  | Files and folders (Yandex Disk)               |

## MCP Client Configuration

### Prerequisites

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (provides `uvx`):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Get a Yandex OAuth token with `wiki:read` / `wiki:write` scopes and your Yandex 360
organization ID. Then add the server to your client using one of the blocks below.

<details>
<summary><b>Claude Code</b></summary>

Add to your project's `.mcp.json` (or run `claude mcp add`):

```json
{
  "mcpServers": {
    "yandex360": {
      "type": "stdio",
      "command": "uvx",
      "args": ["yandex360-mcp@latest"],
      "env": {
        "WIKI_TOKEN": "${WIKI_TOKEN}",
        "WIKI_ORG_ID": "${WIKI_ORG_ID}"
      }
    }
  }
}
```

To track the unreleased `main` branch instead, use
`args`: `["--from", "git+https://github.com/pa1ch/yandex360-mcp@main", "yandex360-mcp"]`.
</details>

<details>
<summary><b>Claude Desktop</b></summary>

Edit `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`):

```json
{
  "mcpServers": {
    "yandex360": {
      "command": "uvx",
      "args": ["yandex360-mcp@latest"],
      "env": {
        "WIKI_TOKEN": "your-oauth-token",
        "WIKI_ORG_ID": "your-org-id"
      }
    }
  }
}
```

Restart Claude Desktop after saving.
</details>

<details>
<summary><b>Cursor</b></summary>

Add to `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "yandex360": {
      "command": "uvx",
      "args": ["yandex360-mcp@latest"],
      "env": {
        "WIKI_TOKEN": "your-oauth-token",
        "WIKI_ORG_ID": "your-org-id"
      }
    }
  }
}
```
</details>

<details>
<summary><b>VS Code / GitHub Copilot</b></summary>

Add to `.vscode/mcp.json`:

```json
{
  "inputs": [
    { "id": "wiki_token", "type": "promptString", "description": "Yandex Wiki OAuth token", "password": true },
    { "id": "wiki_org_id", "type": "promptString", "description": "Yandex 360 organization ID" }
  ],
  "servers": {
    "yandex360": {
      "type": "stdio",
      "command": "uvx",
      "args": ["yandex360-mcp@latest"],
      "env": {
        "WIKI_TOKEN": "${input:wiki_token}",
        "WIKI_ORG_ID": "${input:wiki_org_id}"
      }
    }
  }
}
```
</details>

<details>
<summary><b>Other MCP clients</b></summary>

Any stdio MCP client works. Point it at the command:

```
uvx yandex360-mcp@latest
```

with `WIKI_TOKEN` and `WIKI_ORG_ID` in the environment.
</details>

## Available MCP Tools

<details open>
<summary><b>Wiki</b> (9 tools)</summary>

| Tool | Description |
|------|-------------|
| `wiki_whoami` | Current API user — quick access check |
| `wiki_get_page` | Get a page by `slug` (e.g. `homepage`, `dev/deploy`); optional YFM body |
| `wiki_get_page_by_id` | Get a page by numeric `page_id`; optional YFM body |
| `wiki_tree` | Page tree — descendants of a slug (navigation) |
| `wiki_search` | Full-text search across pages |
| `wiki_create_page` | Create a page (`title`, `slug`, YFM `content`) |
| `wiki_update_page` | Update `title` and/or `content` by id (**replaces** body) |
| `wiki_append_content` | Append YFM content to the end of a page |
| `wiki_delete_page` | Delete a page by id (destructive — confirm first) |

</details>

## Configuration

All configuration is via environment variables — nothing sensitive lives in code or config files.

| Variable           | Module | Required | Description |
|--------------------|--------|----------|-------------|
| `WIKI_TOKEN`       | wiki   | yes\*    | Yandex OAuth token with `wiki:read` / `wiki:write` |
| `WIKI_ORG_ID`      | wiki   | yes\*    | Yandex 360 organization ID (sent as `X-Org-Id`) |
| `YANDEX360_ENABLE` | —      | no       | Comma-separated allow-list of modules (e.g. `wiki`). If unset, every configured module is enabled. |

\* A module activates only when **all** of its variables are set. Unconfigured modules
are skipped (the server logs this to stderr and keeps running).

See [`.env.example`](.env.example) for a template.

## Development

```bash
git clone https://github.com/pa1ch/yandex360-mcp.git
cd yandex360-mcp
uv sync                       # create venv + install deps
uv run yandex360-mcp          # run the server over stdio
uv run pytest                 # run tests
```

### Publishing to PyPI

```bash
uv build                      # wheel + sdist into dist/
uv publish                    # needs a PyPI token (UV_PUBLISH_TOKEN or --token)
```

## Roadmap

- `directory` module — users, departments, org structure (Yandex 360 Directory API).
- `disk` module — file and folder operations (Yandex Disk API).

Contributions welcome — a new service is a single module exposing `is_configured()` and
`register(mcp)`, then one line in the module registry.

## License

[MIT](LICENSE)
