import logging
from urllib.error import HTTPError

from card_identifier.util import download_save_image, retry_if_http_error


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


def test_download_save_image_writes_file(tmp_path, monkeypatch):
    """download_save_image should write the downloaded content to disk."""

    class DummyResponse:
        def __init__(self, content: bytes):
            self.ok = True
            self.content = content

    sample_content = b"fake image data"

    def fake_get(url, allow_redirects=True):
        assert url == "http://example.com/img.png"
        assert allow_redirects is True
        return DummyResponse(sample_content)

    monkeypatch.setattr("card_identifier.util.requests.get", fake_get)

    out_path = tmp_path / "img.png"
    result = download_save_image("http://example.com/img.png", out_path)

    assert result is True
    assert out_path.exists()
    assert out_path.read_bytes() == sample_content
