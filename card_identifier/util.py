import logging
import multiprocessing as mp
import pathlib

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

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


_RETRY = Retry(total=5, status_forcelist=[429], backoff_factor=0.1)
_SESSION = requests.Session()
_SESSION.mount("https://", HTTPAdapter(max_retries=_RETRY))
_SESSION.mount("http://", HTTPAdapter(max_retries=_RETRY))

REQUEST_TIMEOUT = 30


def download_save_image(url: str, path: pathlib.Path) -> bool:
    """Download ``url`` to ``path``, retrying HTTP 429 with exponential backoff."""
    image = _SESSION.get(url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
    logger.debug("downloaded image: %s", url)
    if image.ok:
        with open(path, "wb") as file:
            file.write(image.content)
        logger.info("file written: %s", path)
        return True
    logger.error("error retrieving image: %s", url)
    return False
