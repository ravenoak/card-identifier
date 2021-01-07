import logging
import pathlib
import pickle
from typing import List
from urllib.error import HTTPError

from retrying import retry
import requests
from pokemontcgsdk import Card

from card_identifier.data import get_image_dir, get_pickle_dir

logger = logging.getLogger('card_identifier.pokemon')


def download_card_data() -> List[Card]:
    logger.info('downloading cards')
    all_cards = Card.all()

    path = get_pickle_dir()

    with open(path.joinpath("card-all.pickle"), "wb") as file:
        logger.info('saving card info as pickle')
        pickle.dump(all_cards, file)

    return all_cards


def retry_if_http_error(e: Exception):
    if isinstance(e, HTTPError):
        logger.error(f'HTTP error: {e.code} {e.url}')
        return HTTPError.code == 429


@retry(retry_on_exception=retry_if_http_error,
       wait_exponential_multiplier=100,
       wait_exponential_max=10000)
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


def download_card_images(cards: List[Card], overwrite=False):
    image_dir = get_image_dir()
    id_image_map = {}
    logger.info('downloading card images')
    for card in cards:
        path = image_dir.joinpath(
            ".".join([card.id, card.image_url.split(".")[-1]]))
        if not path.exists() or overwrite:
            if download_save_image(card.image_url, path):
                id_image_map[card.id] = path

    pickle_dir = get_pickle_dir()
    with open(pickle_dir.joinpath("id_image_map.pickle"), "wb") as file:
        logger.info('writing id_image_map as pickle')
        pickle.dump(id_image_map, file)
