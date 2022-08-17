import logging
import pathlib
import pickle
from typing import Dict, List, Union
from urllib.error import HTTPError

from retrying import retry
import requests
from pokemontcgsdk import Card, Set

from card_identifier.data import get_image_dir, get_pickle_dir

logger = logging.getLogger('card_identifier.pokemon')


def refresh_card_data():
    card_path = get_pickle_dir().joinpath("card-all.pickle")
    set_card_path = get_pickle_dir().joinpath("cards_by_set.pickle")

    set_card_map = dict()
    logger.info('downloading cards')
    all_cards = Card.all()
    for card in all_cards:
        if card.set_code not in set_card_map:
            set_card_map[card.set_code] = list()
        set_card_map[card.set_code].append(card)

    with open(card_path, "wb") as file:
        logger.info('saving card info as pickle')
        pickle.dump(all_cards, file)
    with open(set_card_path, "wb") as file:
        logger.info('saving set-card map as pickle')
        pickle.dump(set_card_map, file)


def refresh_set_data():
    path = get_pickle_dir().joinpath("set-all.pickle")

    logger.info('downloading sets')
    all_sets = Set.all()

    with open(path, "wb") as file:
        logger.info('saving set info as pickle')
        pickle.dump(all_sets, file)


def get_card_data(flat=False) -> Union[Dict, List[Card]]:
    card_path = get_pickle_dir().joinpath("card-all.pickle")
    set_card_path = get_pickle_dir().joinpath("cards_by_set.pickle")

    if flat:
        with open(card_path, "rb") as file:
            all_cards = pickle.load(file)
        return all_cards
    else:
        with open(set_card_path, "rb") as file:
            cards_by_set = pickle.load(file)
        return cards_by_set


def get_set_data() -> List[Set]:
    path = get_pickle_dir().joinpath("set-all.pickle")

    with open(path, "rb") as file:
        all_sets = pickle.load(file)

    return all_sets


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
