"""Тонкий HTTP-клиент для API Яндекс 360 поверх стандартной библиотеки.

Один класс на все сервисы: у них общая схема авторизации (OAuth-токен в заголовке
``Authorization`` и ID организации в ``X-Org-Id``), различаются лишь базовый URL и
пути. Namespace-модули (wiki, directory, …) создают свой ``ApiClient`` со своим
base_url и токеном и дёргают ``request``. Никаких тяжёлых зависимостей — только
urllib, чтобы пакет ставился через ``uvx`` мгновенно.
"""

from __future__ import annotations

import contextlib
import json
import urllib.error
import urllib.parse
import urllib.request


class ApiClient:
    """Клиент к одному сервису Яндекс 360.

    Args:
        base_url: базовый URL API сервиса (напр. ``https://api.wiki.yandex.net``).
        token: OAuth-токен Яндекса с нужными правами.
        org_id: ID организации Яндекс 360 (заголовок ``X-Org-Id``); может быть пустым
            для сервисов, которым он не нужен.
        timeout: таймаут запроса в секундах.
    """

    def __init__(self, base_url: str, token: str, org_id: str = "", *, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.org_id = org_id
        self.timeout = timeout

    def request(
        self, method: str, path: str, *, params: dict | None = None, body: dict | None = None
    ) -> dict:
        """Выполнить запрос и вернуть распарсенный JSON (или ``{'error': ...}``).

        Ошибки не бросаются, а возвращаются словарём — так модели удобнее их читать
        и реагировать, чем ловить traceback транспорта.
        """
        url = f"{self.base_url}{path}"
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                url += "?" + urllib.parse.urlencode(clean)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"OAuth {self.token}")
        if self.org_id:
            req.add_header("X-Org-Id", str(self.org_id))
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode() or "{}"
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            with contextlib.suppress(Exception):
                detail = json.loads(detail)
            return {"error": f"HTTP {e.code}", "detail": detail}
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}
