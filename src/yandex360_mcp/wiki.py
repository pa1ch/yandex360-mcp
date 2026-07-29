"""Модуль Яндекс Вики (Yandex Wiki Public API 1.0.0).

Инструменты для чтения и правки страниц вики организации Яндекс 360. Формат тела
страниц — YFM (Yandex Flavored Markdown). Базовый URL: https://api.wiki.yandex.net/v1

Окружение:
    WIKI_TOKEN   — OAuth-токен Яндекса (право wiki:read / wiki:write)
    WIKI_ORG_ID  — ID организации Яндекс 360 (заголовок X-Org-Id)
"""

from __future__ import annotations

import os

from mcp.server.mcpserver import MCPServer

from ._http import ApiClient

API_BASE = "https://api.wiki.yandex.net"


def is_configured() -> bool:
    """Заданы ли оба токена модуля в окружении (иначе модуль не регистрируется)."""
    return bool(os.environ.get("WIKI_TOKEN") and os.environ.get("WIKI_ORG_ID"))


def register(mcp: MCPServer) -> None:
    """Зарегистрировать инструменты Вики в переданном сервере MCPServer."""
    client = ApiClient(API_BASE, os.environ.get("WIKI_TOKEN", ""), os.environ.get("WIKI_ORG_ID", ""))

    @mcp.tool()
    def wiki_whoami() -> dict:
        """Кто я: данные текущего пользователя API Вики (проверка доступа)."""
        return client.request("GET", "/v1/users/me")

    @mcp.tool()
    def wiki_get_page(slug: str, with_content: bool = True) -> dict:
        """Получить страницу по её slug (адресу, напр. 'homepage' или 'razrabotka/deploy').

        with_content=True добавляет тело страницы в формате YFM (поле content).
        """
        params = {"slug": slug}
        if with_content:
            params["fields"] = "content"
        return client.request("GET", "/v1/pages", params=params)

    @mcp.tool()
    def wiki_get_page_by_id(page_id: int, with_content: bool = True) -> dict:
        """Получить страницу по числовому id. with_content=True — вернуть тело (YFM)."""
        params = {"fields": "content"} if with_content else None
        return client.request("GET", f"/v1/pages/{page_id}", params=params)

    @mcp.tool()
    def wiki_tree(slug: str = "homepage", page_size: int = 100) -> dict:
        """Дерево страниц: все потомки страницы с данным slug (для навигации по вики).

        По умолчанию — от корневой 'homepage'. Личные разделы пользователей — slug 'users'.
        """
        return client.request(
            "GET",
            "/v1/pages/descendants",
            params={"slug": slug, "include_self": True, "page_size": page_size},
        )

    @mcp.tool()
    def wiki_search(query: str, page_size: int = 20) -> dict:
        """Полнотекстовый поиск по страницам вики. Возвращает совпадения с id и slug."""
        return client.request(
            "POST",
            "/v1/search",
            body={"query": query, "page_size": page_size, "highlight": True},
        )

    @mcp.tool()
    def wiki_create_page(title: str, slug: str, content: str = "") -> dict:
        """Создать страницу. title — заголовок, slug — адрес (напр. 'razrabotka/notes'),
        content — тело в формате YFM. Родитель определяется префиксом slug.
        """
        return client.request(
            "POST",
            "/v1/pages",
            params={"fields": "content"},
            body={"title": title, "slug": slug, "content": content},
        )

    @mcp.tool()
    def wiki_update_page(
        page_id: int, title: str | None = None, content: str | None = None
    ) -> dict:
        """Обновить страницу по id. Передавай только то, что меняешь: title и/или content (YFM).

        ВНИМАНИЕ: content полностью ЗАМЕНЯЕТ текущее тело страницы. Чтобы дописать в конец,
        используй wiki_append_content. Перед заменой разумно сначала прочитать текущий content.
        """
        body: dict = {}
        if title is not None:
            body["title"] = title
        if content is not None:
            body["content"] = content
        if not body:
            return {"error": "нужно передать хотя бы title или content"}
        return client.request(
            "POST", f"/v1/pages/{page_id}", params={"fields": "content"}, body=body
        )

    @mcp.tool()
    def wiki_append_content(page_id: int, content: str) -> dict:
        """Дописать content (YFM) в конец страницы, не затрагивая существующий текст."""
        return client.request(
            "POST",
            f"/v1/pages/{page_id}/append-content",
            params={"fields": "content"},
            body={"content": content},
        )

    @mcp.tool()
    def wiki_delete_page(page_id: int) -> dict:
        """Удалить страницу по id. Действие деструктивное — сначала уточни у пользователя."""
        return client.request("DELETE", f"/v1/pages/{page_id}")
