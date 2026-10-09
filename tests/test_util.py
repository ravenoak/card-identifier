import http.server
import threading

import pytest

from card_identifier.util import download_save_image


@pytest.fixture
def server():
    """Serve /img.png: 429 for the first ``fail_count`` requests, then 200."""

    class Handler(http.server.BaseHTTPRequestHandler):
        hits = 0
        fail_count = 0

        def do_GET(self):
            type(self).hits += 1
            if type(self).hits <= type(self).fail_count:
                self.send_response(429)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            body = b"fake image data"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield Handler, f"http://127.0.0.1:{httpd.server_port}/img.png"
    httpd.shutdown()
    httpd.server_close()
    thread.join()


def test_download_save_image_writes_file(tmp_path, server):
    handler, url = server
    out_path = tmp_path / "img.png"

    assert download_save_image(url, out_path) is True

    assert out_path.read_bytes() == b"fake image data"
    assert handler.hits == 1


def test_download_save_image_retries_on_429(tmp_path, server):
    handler, url = server
    handler.fail_count = 2
    out_path = tmp_path / "img.png"

    assert download_save_image(url, out_path) is True

    assert out_path.read_bytes() == b"fake image data"
    assert handler.hits == 3


def test_download_save_image_returns_false_on_http_error(tmp_path):
    out_path = tmp_path / "img.png"

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, format, *args):
            pass

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{httpd.server_port}/missing.png"
        assert download_save_image(url, out_path) is False
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join()

    assert not out_path.exists()
