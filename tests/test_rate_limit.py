"""
Per-user rate limiting on Gemini-backed endpoints.
"""

from fastapi.testclient import TestClient
from main import app
from rate_limit import limiter, UserRateLimiter


def _chat(client, headers):
    return client.post(
        "/api/forecast/chat",
        json={"scenario_id": "saas_finops", "message": "hi", "history": []},
        headers=headers,
    )


def test_limiter_blocks_after_per_minute_limit(monkeypatch):
    monkeypatch.setenv("CHAT_RATE_PER_MIN", "3")
    monkeypatch.setenv("CHAT_RATE_PER_DAY", "0")
    rl = UserRateLimiter()
    assert all(rl.check("u1", now=1000.0 + i) is None for i in range(3))
    retry = rl.check("u1", now=1003.0)
    assert retry is not None and 1 <= retry <= 60
    assert rl.check("u2", now=1003.0) is None  # other users unaffected
    assert rl.check("u1", now=1061.0) is None  # window slides


def test_limiter_enforces_daily_limit(monkeypatch):
    monkeypatch.setenv("CHAT_RATE_PER_MIN", "0")
    monkeypatch.setenv("CHAT_RATE_PER_DAY", "2")
    rl = UserRateLimiter()
    assert rl.check("u1", now=0.0) is None
    assert rl.check("u1", now=100.0) is None
    assert rl.check("u1", now=200.0) is not None
    assert rl.check("u1", now=86401.0) is None


def test_limiter_disabled_when_limits_zero(monkeypatch):
    monkeypatch.setenv("CHAT_RATE_PER_MIN", "0")
    monkeypatch.setenv("CHAT_RATE_PER_DAY", "0")
    rl = UserRateLimiter()
    assert all(rl.check("u1", now=1.0) is None for _ in range(500))


def test_chat_endpoint_returns_429_with_retry_after(monkeypatch, demo_auth_headers):
    monkeypatch.setenv("CHAT_RATE_PER_MIN", "2")
    monkeypatch.setenv("CHAT_RATE_PER_DAY", "0")
    limiter.reset()
    client = TestClient(app)
    try:
        assert _chat(client, demo_auth_headers).status_code == 200
        assert _chat(client, demo_auth_headers).status_code == 200
        res = _chat(client, demo_auth_headers)
        assert res.status_code == 429
        assert int(res.headers["Retry-After"]) >= 1
    finally:
        limiter.reset()


def test_unauthenticated_request_is_401_not_429(monkeypatch):
    monkeypatch.setenv("CHAT_RATE_PER_MIN", "1")
    limiter.reset()
    client = TestClient(app)
    for _ in range(3):
        res = client.post("/api/forecast/chat", json={"scenario_id": "saas_finops", "message": "hi"})
        assert res.status_code in (401, 403)
