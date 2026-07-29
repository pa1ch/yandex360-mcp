"""Тесты сборки сервера.

Главное здесь — импорт и регистрация инструментов происходят по-настоящему. Именно
такой тест ловит поломки SDK вида «модуль переехал» (mcp 2.0 убрал
``mcp.server.fastmcp``), которые иначе всплывают только у пользователя: клиент MCP
молча выкидывает упавший на импорте сервер из списка.
"""

from __future__ import annotations

import asyncio

from yandex360_mcp.server import MODULES, build_server


def _tool_names(server) -> set[str]:
    return {t.name for t in asyncio.run(server.list_tools())}


def _configure_wiki(monkeypatch) -> None:
    monkeypatch.setenv("WIKI_TOKEN", "dummy-token")
    monkeypatch.setenv("WIKI_ORG_ID", "42")
    monkeypatch.delenv("YANDEX360_ENABLE", raising=False)


def test_build_server_registers_wiki_tools(monkeypatch):
    """С заданными токенами модуль wiki регистрирует свои инструменты."""
    _configure_wiki(monkeypatch)
    names = _tool_names(build_server())
    assert "wiki_whoami" in names
    assert "wiki_get_page" in names
    assert "wiki_delete_page" in names


def test_module_without_tokens_is_skipped(monkeypatch):
    """Без токенов модуль не регистрируется — инструментов нет вовсе."""
    monkeypatch.delenv("WIKI_TOKEN", raising=False)
    monkeypatch.delenv("WIKI_ORG_ID", raising=False)
    monkeypatch.delenv("YANDEX360_ENABLE", raising=False)
    assert _tool_names(build_server()) == set()


def test_enable_switch_filters_modules(monkeypatch):
    """YANDEX360_ENABLE со сторонним именем отключает даже настроенный модуль."""
    _configure_wiki(monkeypatch)
    monkeypatch.setenv("YANDEX360_ENABLE", "directory")
    assert _tool_names(build_server()) == set()


def test_every_module_exposes_the_expected_interface():
    """Контракт реестра: у каждого модуля есть is_configured() и register()."""
    for name, module in MODULES.items():
        assert callable(module.is_configured), name
        assert callable(module.register), name


def test_tool_schemas_are_generated(monkeypatch):
    """У инструментов есть описание и схема аргументов — то, что видит модель."""
    _configure_wiki(monkeypatch)
    tools = {t.name: t for t in asyncio.run(build_server().list_tools())}

    get_page = tools["wiki_get_page"]
    assert get_page.description
    assert set(get_page.input_schema["properties"]) == {"slug", "with_content"}
    assert get_page.input_schema["required"] == ["slug"]
