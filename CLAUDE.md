# CLAUDE.md — гайд для ассистента

Публичный пакет **yandex360-mcp** — модульный MCP-сервер для сервисов Яндекс 360
(сейчас модуль `wiki`). Опубликован на PyPI, GitHub и в MCP Registry.

> **Релизы разработчик вручную не делает — релиз целиком проводит ассистент по запросу**
> («выпусти патч», «сделай релиз 0.2.0»). Ниже — процедура; следуй ей.

## Как устроен релиз (всё автоматически по тегу)

Пуш тега `vX.Y.Z` запускает `.github/workflows/release.yml`, который сам:
- собирает пакет и гоняет тесты, сверяет `тег == version в pyproject.toml`;
- публикует на **PyPI** (Trusted Publishing / OIDC, без токена);
- собирает **`.mcpb`**-бандл и прикладывает к GitHub Release (вместе с wheel и sdist);
- публикует в **MCP Registry** (`mcp-publisher login github-oidc`);
- подставляет версию из тега в `server.json` и `manifest.json`.

Ничего из этого руками не делаем: **ни `uv publish`, ни `mcp-publisher`, ни создание
GitHub Release** — только тег.

## Процедура релиза (шаги ассистента)

1. Выбрать версию по SemVer: **patch** — фиксы; **minor** — новый модуль/фича;
   **major** — ломающие изменения.
2. Поднять версию **ровно в двух файлах**: `pyproject.toml` и
   `src/yandex360_mcp/__init__.py`. (`server.json` и `manifest.json` CI выставит из
   тега; бампать их не обязательно, но и не вредно.)
3. `CHANGELOG.md`: перенести пункты из `## [Unreleased]` в `## [X.Y.Z] - <сегодня>`,
   оставить `[Unreleased]` пустым.
4. Локальная проверка: `uv build` и `uv run pytest -q`; по желанию
   `npx --yes @anthropic-ai/mcpb validate manifest.json`.
5. Коммит в `main` и пуш.
6. Тег и пуш тега:
   ```
   git tag vX.Y.Z && git push origin vX.Y.Z
   ```
7. Дождаться пайплайна и проверить результат:
   ```
   gh run watch <run-id> --exit-status
   gh release view vX.Y.Z --json assets      # .mcpb + wheel + sdist
   ```
   В логе job `mcp-registry` должна быть строка
   `✓ Successfully published ... version X.Y.Z`.

## Гарды

- **Тег обязан совпадать с версией в `pyproject.toml`** — иначе job `build` падает на
  сверке (это защита от рассинхрона).
- **Версии на PyPI неизменяемы.** Никогда не переиспользуй номер — только вверх. Если
  релиз частично упал уже после публикации на PyPI, этот номер «сгорел» → почини и
  выпусти следующий патч.
- Коммиты и PR — **без любых упоминаний Claude/AI** (`Co-Authored-By` и т.п.).
- Trusted Publisher на PyPI и доверие OIDC для namespace `io.github.pa1ch` уже настроены —
  доп. действий не требуют.

## Архитектура (кратко)

- Модуль на сервис в `src/yandex360_mcp/<service>.py` с `is_configured()` и
  `register(mcp)`; реестр модулей — в `server.py` (`MODULES`).
- Модуль регистрирует инструменты, только если заданы все его env-токены и он не исключён
  через `YANDEX360_ENABLE` (экономия контекста модели).
- Новый сервис = новый модуль + одна строка в `MODULES` + запись в `README`/`manifest.json`.

## Разовая настройка (уже сделана, для справки)

- PyPI → проект `yandex360-mcp` → Publishing → Trusted Publisher: repo
  `pa1ch/yandex360-mcp`, workflow `release.yml`, environment `pypi`.
- MCP Registry доверяет GitHub Actions OIDC для `io.github.pa1ch` автоматически.
