"""Тесты HTTP-клиента: сборка URL/заголовков и обработка ошибок — без реальной сети."""

from __future__ import annotations

import io
import json
import urllib.error

from yandex360_mcp._http import ApiClient


class _Resp(io.BytesIO):
    """Заглушка ответа urlopen с поддержкой контекст-менеджера."""

    def __enter__(self) -> "_Resp":
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def test_request_builds_url_and_headers(monkeypatch) -> None:
    captured: dict = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["headers"] = {k.lower(): v for k, v in req.header_items()}
        return _Resp(json.dumps({"ok": True}).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = ApiClient("https://api.wiki.yandex.net", "T0KEN", "42")
    out = client.request("GET", "/v1/pages", params={"slug": "home", "skip": None})

    assert out == {"ok": True}
    # None-параметры отфильтровываются, остаётся только slug
    assert captured["url"] == "https://api.wiki.yandex.net/v1/pages?slug=home"
    assert captured["method"] == "GET"
    assert captured["headers"]["authorization"] == "OAuth T0KEN"
    assert captured["headers"]["x-org-id"] == "42"


def test_post_sets_json_body_and_content_type(monkeypatch) -> None:
    captured: dict = {}

    def fake_urlopen(req, timeout=None):
        captured["body"] = req.data
        captured["headers"] = {k.lower(): v for k, v in req.header_items()}
        return _Resp(b"{}")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = ApiClient("https://x", "T", "1")
    client.request("POST", "/v1/search", body={"query": "abc"})

    assert json.loads(captured["body"]) == {"query": "abc"}
    assert captured["headers"]["content-type"] == "application/json"


def test_http_error_returns_parsed_detail(monkeypatch) -> None:
    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(
            req.full_url, 404, "Not Found", {}, io.BytesIO(b'{"message": "no such page"}')
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = ApiClient("https://x", "T", "1")
    out = client.request("GET", "/v1/pages/999")

    assert out["error"] == "HTTP 404"
    assert out["detail"] == {"message": "no such page"}


def test_empty_body_parses_as_empty_dict(monkeypatch) -> None:
    def fake_urlopen(req, timeout=None):
        return _Resp(b"")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = ApiClient("https://x", "T", "1")
    assert client.request("DELETE", "/v1/pages/1") == {}
