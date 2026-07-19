# MCP-сервер Яндекс 360

[![PyPI version](https://img.shields.io/pypi/v/yandex360-mcp.svg)](https://pypi.org/project/yandex360-mcp/)
[![Tests](https://github.com/pa1ch/yandex360-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/pa1ch/yandex360-mcp/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

MCP-сервер, который даёт AI-ассистентам (Claude Code, Claude Desktop, Cursor, VS Code и
любому MCP-клиенту) инструменты для работы с сервисами организации
**[Яндекс 360](https://360.yandex.ru/)** — начиная с **Яндекс Вики**. Транспорт —
**stdio**, единственная зависимость — `mcp`, ставится и запускается через `uvx` без
клонирования.

🇬🇧 English docs — [README.md](README.md).

> **Область:** сервер покрывает сервисы **Яндекс 360** (Вики, далее Директория, Диск).
> **Яндекс Трекер намеренно вне области** — для него есть отличный зрелый сервер
> **[aikts/yandex-tracker-mcp](https://github.com/aikts/yandex-tracker-mcp)**.
> Используйте их вместе.

## Возможности

- 📖 **Яндекс Вики** — чтение и правка страниц (YFM), полнотекстовый поиск, навигация по дереву, создание / обновление / дозапись / удаление.
- 🧩 **Модульность по сервисам** — каждый сервис Яндекс 360 это отдельный модуль. Модуль регистрирует инструменты, **только если заданы его токены**, поэтому модель не получает инструменты неиспользуемых сервисов — контекст остаётся лёгким.
- 🔌 **Установка без трения** — одна зависимость, транспорт stdio, запуск через `uvx` прямо из GitHub или с PyPI.
- 🔐 **Никаких секретов в коде и конфиге** — все токены только из переменных окружения.

### Модули

| Модуль      | Статус       | Описание                                     |
|-------------|--------------|----------------------------------------------|
| `wiki`      | ✅ готов      | Чтение/правка страниц Яндекс Вики (YFM)      |
| `directory` | 🔜 в планах  | Пользователи и оргструктура (Яндекс 360)     |
| `disk`      | 🔜 в планах  | Файлы и папки (Яндекс Диск)                   |

## Подключение к MCP-клиенту

### Предпосылки

Установите [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (даёт `uvx`):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Получите OAuth-токен Яндекса с правами `wiki:read` / `wiki:write` и ID своей
организации Яндекс 360. Затем добавьте сервер в клиент одним из блоков ниже.

<details>
<summary><b>Claude Code</b></summary>

В `.mcp.json` проекта (или `claude mcp add`):

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

Чтобы брать свежий `main` вместо релиза, используй
`args`: `["--from", "git+https://github.com/pa1ch/yandex360-mcp@main", "yandex360-mcp"]`.
</details>

<details>
<summary><b>Claude Desktop</b></summary>

Правим `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`):

```json
{
  "mcpServers": {
    "yandex360": {
      "command": "uvx",
      "args": ["yandex360-mcp@latest"],
      "env": {
        "WIKI_TOKEN": "ваш-oauth-токен",
        "WIKI_ORG_ID": "ваш-org-id"
      }
    }
  }
}
```

После сохранения перезапустите Claude Desktop.
</details>

<details>
<summary><b>Cursor</b></summary>

В `.cursor/mcp.json` (проект) или `~/.cursor/mcp.json` (глобально):

```json
{
  "mcpServers": {
    "yandex360": {
      "command": "uvx",
      "args": ["yandex360-mcp@latest"],
      "env": {
        "WIKI_TOKEN": "ваш-oauth-токен",
        "WIKI_ORG_ID": "ваш-org-id"
      }
    }
  }
}
```
</details>

<details>
<summary><b>VS Code / GitHub Copilot</b></summary>

В `.vscode/mcp.json`:

```json
{
  "inputs": [
    { "id": "wiki_token", "type": "promptString", "description": "OAuth-токен Яндекс Вики", "password": true },
    { "id": "wiki_org_id", "type": "promptString", "description": "ID организации Яндекс 360" }
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
<summary><b>Другие MCP-клиенты</b></summary>

Подойдёт любой stdio-клиент. Команда запуска:

```
uvx yandex360-mcp@latest
```

с `WIKI_TOKEN` и `WIKI_ORG_ID` в окружении.
</details>

## Доступные инструменты

<details open>
<summary><b>Вики</b> (9 инструментов)</summary>

| Инструмент | Описание |
|------------|----------|
| `wiki_whoami` | Текущий пользователь API — быстрая проверка доступа |
| `wiki_get_page` | Страница по `slug` (напр. `homepage`, `dev/deploy`); опц. тело YFM |
| `wiki_get_page_by_id` | Страница по числовому `page_id`; опц. тело YFM |
| `wiki_tree` | Дерево страниц — потомки slug (навигация) |
| `wiki_search` | Полнотекстовый поиск по страницам |
| `wiki_create_page` | Создать страницу (`title`, `slug`, тело YFM `content`) |
| `wiki_update_page` | Обновить `title` и/или `content` по id (**заменяет** тело) |
| `wiki_append_content` | Дописать YFM-контент в конец страницы |
| `wiki_delete_page` | Удалить страницу по id (деструктивно — сначала подтвердить) |

</details>

## Конфигурация

Вся конфигурация — через переменные окружения; ничего секретного в коде и конфигах нет.

| Переменная         | Модуль | Обязательна | Описание |
|--------------------|--------|-------------|----------|
| `WIKI_TOKEN`       | wiki   | да\*        | OAuth-токен Яндекса с правами `wiki:read` / `wiki:write` |
| `WIKI_ORG_ID`      | wiki   | да\*        | ID организации Яндекс 360 (заголовок `X-Org-Id`) |
| `YANDEX360_ENABLE` | —      | нет         | Список модулей через запятую (напр. `wiki`). Не задан — включаются все сконфигурированные. |

\* Модуль активируется, только если заданы **все** его переменные. Несконфигурированные
модули пропускаются (сервер пишет об этом в stderr и продолжает работу).

Шаблон — в [`.env.example`](.env.example).

## Загрузка только нужных модулей

Каждый зарегистрированный инструмент занимает место в контексте модели, поэтому сервер
отдаёт **только те модули, которые ты реально сконфигурировал** — остальное до модели не
доходит. На старте инструменты модуля регистрируются, **только если выполнены оба**
условия:

1. **заданы все переменные окружения модуля** (напр. `wiki` требует `WIKI_TOKEN`
   **и** `WIKI_ORG_ID`), **и**
2. модуль **не исключён** через `YANDEX360_ENABLE`.

Два способа управлять набором инструментов:

- **Через конфигурацию (по умолчанию).** Задавай токены только для нужных сервисов.
  Модуль без своих переменных молча пропускается. Настроил только `wiki` → в контексте
  ровно девять `wiki_*` инструментов и ничего от `directory` / `disk`.
- **Через явный allow-list.** Укажи `YANDEX360_ENABLE` списком через запятую, чтобы
  зафиксировать точное подмножество, даже если сконфигурировано больше — напр.
  `YANDEX360_ENABLE=wiki`.

На старте сервер пишет в stderr, какие модули активны (и какие пропущены).

> **Агентам, которые ставят этот сервер:** держи набор инструментов минимальным —
> конфигурируй **только** те сервисы, которые реально нужны пользователю. Дай токены
> лишь этих модулей (и/или зафиксируй `YANDEX360_ENABLE`). **Не** добавляй токены
> сервисов, которые не будут использоваться: каждый лишний модуль грузит инструменты,
> которые только засоряют контекст модели.

## Разработка

```bash
git clone https://github.com/pa1ch/yandex360-mcp.git
cd yandex360-mcp
uv sync                       # окружение + зависимости
uv run yandex360-mcp          # запустить сервер (stdio)
uv run pytest                 # тесты
```

### Публикация на PyPI

```bash
uv build                      # wheel + sdist в dist/
uv publish                    # нужен токен PyPI (UV_PUBLISH_TOKEN или --token)
```

## Планы

- Модуль `directory` — пользователи, отделы, оргструктура (Yandex 360 Directory API).
- Модуль `disk` — работа с файлами и папками (Yandex Disk API).

Новый сервис — это один модуль с `is_configured()` и `register(mcp)` плюс строка в реестре модулей. PR приветствуются.

## Лицензия

[MIT](LICENSE)
