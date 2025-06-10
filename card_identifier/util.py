import logging
import multiprocessing as mp
import pathlib
from urllib.error import HTTPError

import requests
from retrying import retry

logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    fmt = "%(asctime)s - %(processName)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=fmt, level=level)

    mp_logger = mp.get_logger()
    mp_logger.setLevel(level)
    if not mp_logger.handlers:
        for handler in logging.getLogger().handlers:
            mp_logger.addHandler(handler)


def retry_if_http_error(e: Exception):
    if isinstance(e, HTTPError):
        logger.error(f"HTTP error: {e.code} {e.url}")
        return e.code == 429


@retry(
    retry_on_exception=retry_if_http_error,
    wait_exponential_multiplier=100,
    wait_exponential_max=10000,
)
def download_save_image(url: str, path: pathlib.Path) -> bool:
    image = requests.get(url, allow_redirects=True)
    logger.debug(f"downloaded image: {url}")
    if image.ok:
        with open(path, "wb") as file:
            file.write(image.content)
        logger.info(f"file written: {path}")
        return True
    else:
        logger.error(f"error retrieving image: {url}")
        return False
