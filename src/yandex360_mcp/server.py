"""Сборка сервера: подключает модули сервисов по наличию токенов и env-переключателю.

Каждый модуль (wiki, …) объявляет ``is_configured()`` и ``register(mcp)``. Модуль
активируется, только если он сконфигурирован и не отключён через ``YANDEX360_ENABLE``.
Это и есть механизм экономии контекста: модель получает инструменты лишь включённых
сервисов, а не весь пакет.
"""

from __future__ import annotations

import os
import sys

from mcp.server.fastmcp import FastMCP

from . import wiki

# Реестр модулей сервисов: имя -> модуль. Новый сервис добавляется одной строкой.
MODULES = {
    "wiki": wiki,
}


def _enabled_names() -> set[str] | None:
    """Разобрать YANDEX360_ENABLE (список через запятую). None — ограничений нет."""
    raw = os.environ.get("YANDEX360_ENABLE", "").strip()
    if not raw:
        return None
    return {name.strip() for name in raw.split(",") if name.strip()}


def build_server() -> FastMCP:
    """Создать FastMCP и зарегистрировать в нём активные модули сервисов."""
    mcp = FastMCP("yandex360")
    enabled = _enabled_names()
    active: list[str] = []
    for name, module in MODULES.items():
        if enabled is not None and name not in enabled:
            continue
        if not module.is_configured():
            print(
                f"[yandex360-mcp] модуль '{name}' пропущен: не заданы токены в окружении",
                file=sys.stderr,
            )
            continue
        module.register(mcp)
        active.append(name)

    if active:
        print(f"[yandex360-mcp] активные модули: {', '.join(active)}", file=sys.stderr)
    else:
        print(
            "[yandex360-mcp] ВНИМАНИЕ: ни один модуль не активирован — проверь env-токены",
            file=sys.stderr,
        )
    return mcp
