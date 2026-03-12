from pathlib import Path

import pytest

from app.clients.kalshi_auth import (
    KalshiAuth,
    build_auth_headers,
    build_signature_payload,
    sign_request,
)


def test_signature_payload_excludes_query() -> None:
    payload = build_signature_payload("123", "get", "/markets?limit=10")
    assert payload == "123GET/markets"


def test_signature_payload_normalizes_missing_leading_slash() -> None:
    payload = build_signature_payload("123", "get", "markets?limit=10")
    assert payload == "123GET/markets"


def test_sign_request_is_deterministic(tmp_path: Path) -> None:
    key = tmp_path / "key.pem"
    key.write_text("dummy-private-key")
    s1 = sign_request(timestamp="1", method="GET", path="/markets", private_key_path=str(key))
    s2 = sign_request(timestamp="1", method="GET", path="/markets", private_key_path=str(key))
    assert s1 == s2


def test_build_auth_headers_from_private_key(tmp_path: Path) -> None:
    key = tmp_path / "key.pem"
    key.write_text("private-signing-key")

    headers = build_auth_headers(
        key_id="kid",
        timestamp="123",
        method="GET",
        path="/markets?cursor=x",
        private_key_path=str(key),
    )
    assert headers.key == "kid"
    assert headers.timestamp == "123"
    assert headers.signature


def test_sign_fails_closed_with_missing_credentials() -> None:
    auth = KalshiAuth(access_key="", signing_key="")
    with pytest.raises(ValueError):
        auth.sign("GET", "/markets", timestamp_ms=123)


def test_sign_request_requires_key_source() -> None:
    with pytest.raises(ValueError):
        sign_request(timestamp="1", method="GET", path="/markets")
