from pathlib import Path

from app.clients.kalshi_auth import build_signature_payload, sign_request


def test_signature_payload_excludes_query() -> None:
    payload = build_signature_payload("123", "get", "/markets?limit=10")
    assert payload == "123GET/markets"


def test_sign_request_is_deterministic(tmp_path: Path) -> None:
    key = tmp_path / "key.pem"
    key.write_text("dummy-private-key")
    s1 = sign_request(timestamp="1", method="GET", path="/markets", private_key_path=str(key))
    s2 = sign_request(timestamp="1", method="GET", path="/markets", private_key_path=str(key))
    assert s1 == s2
