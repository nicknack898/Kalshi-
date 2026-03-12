from datetime import datetime, timezone

from app.clients.historical_router import route_endpoint


def test_routes_to_historical_when_before_cutoff() -> None:
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    decision = route_endpoint(base_path="/markets", query_start=start, cutoff_timestamp_ms=1710000000000)
    assert decision.use_historical
    assert decision.endpoint_path == "/historical/markets"
