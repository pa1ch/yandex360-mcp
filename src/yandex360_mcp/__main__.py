"""Точка входа: собрать сервер и запустить по stdio."""

from __future__ import annotations

from .server import build_server


def main() -> None:
    """Entry-point консольной команды ``yandex360-mcp``."""
    build_server().run()


if __name__ == "__main__":
    main()
