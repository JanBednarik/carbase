from datetime import date


from app.models.api_token import ApiToken


def test_token_is_long():
    token = ApiToken(name="test")
    assert len(token.token) >= 32


def test_tokens_are_unique():
    token1 = ApiToken(name="first")
    token2 = ApiToken(name="second")
    assert token1.token != token2.token


def test_expires_at_default(mocker):
    mocker.patch("app.models.api_token.date").today.return_value = date(2026, 1, 1)
    token = ApiToken(name="test")
    assert token.expires_at == date(2026, 3, 7)  # 2026-01-01 + 65 days


def test_expires_at_custom_env(mocker, monkeypatch):
    mocker.patch("app.models.api_token.date").today.return_value = date(2026, 1, 1)
    monkeypatch.setenv("TOKEN_EXPIRATION_DAYS", "30")
    token = ApiToken(name="test")
    assert token.expires_at == date(2026, 1, 31)  # 2026-01-01 + 30 days
