import base64
import hashlib
import hmac

from app.clients.kalshi_auth import KalshiAuth


def test_sign_uses_expected_payload_and_signature() -> None:
    auth = KalshiAuth(access_key="ak", signing_key="secret")
    headers = auth.sign("get", "/trade-api/v2/markets", timestamp_ms=1700000000000)

    expected_payload = "1700000000000GET/trade-api/v2/markets"
    expected_signature = base64.b64encode(
        hmac.new(b"secret", expected_payload.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")

    assert headers["KALSHI-ACCESS-KEY"] == "ak"
    assert headers["KALSHI-ACCESS-TIMESTAMP"] == "1700000000000"
    assert headers["KALSHI-ACCESS-SIGNATURE"] == expected_signature
