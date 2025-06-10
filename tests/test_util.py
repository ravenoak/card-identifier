import logging
from urllib.error import HTTPError

from card_identifier.util import retry_if_http_error


def test_retry_if_http_error_returns_true_on_429(caplog):
    err = HTTPError(
        url="http://example.com", code=429, msg="Too Many Requests", hdrs=None, fp=None
    )
    caplog.set_level(logging.ERROR)
    assert retry_if_http_error(err) is True
    assert any(
        "HTTP error: 429 http://example.com" in record.message
        for record in caplog.records
    )
