import logging
import pathlib
from urllib.error import HTTPError

import requests
from retrying import retry

logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False):
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=level,
    )


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
