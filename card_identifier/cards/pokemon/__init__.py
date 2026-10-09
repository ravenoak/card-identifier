import logging
import pathlib
from collections.abc import Iterable
from functools import lru_cache

from pokemontcgsdk import Card, Set

from card_identifier.cards.base import BaseCardManager
from card_identifier.data import get_image_dir, get_pickle_dir
from card_identifier.storage import load_pickle, save_pickle
from card_identifier.util import download_save_image

from .api_client import CardAPIClient, PokemonTCGSDKClient

logger = logging.getLogger("card_identifier.pokemon")


@lru_cache(maxsize=1)
def get_legal_sets():
    """Return the set IDs that are legal in Standard or Expanded play."""

    return {s.id for s in Set.where(q="legalities.standard:legal")} | {
        s.id for s in Set.where(q="legalities.expanded:legal")
    }


class ImageManager:
    """Manages the original images for the Pokémon TCG"""

    def __init__(self):
        self.pickle_dir = get_pickle_dir("pokemon")
        self.image_dir = get_image_dir("pokemon")
        self.card_image_file = self.pickle_dir.joinpath("card_image_map.pickle")
        self.card_image_map = self.load_card_image_map()

    def scan_img_dir(self) -> dict[str, str]:
        """Creates a map of card id to image path for all images in the image_dir"""
        card_image_map = {}
        for img in self.image_dir.glob("**/*.png"):
            card_image_map[img.stem] = img.name
        return card_image_map

    def load_card_image_map(self) -> dict[str, str]:
        """Loads the card_image_map pickle if it exists, otherwise returns an empty dict"""
        if self.card_image_file.exists():
            logger.info("opening card_image_map pickle")
            return load_pickle(self.card_image_file, default={})
        logger.info("not loading card_image_map: missing")
        return {}

    def save_card_image_map(self):
        """Saves the card_image_map pickle"""
        logger.info("saving card_image_map pickle")
        save_pickle(self.card_image_map, self.card_image_file)

    def refresh_card_image_map(self):
        """Refreshes the card_image_map pickle"""
        self.card_image_map = self.scan_img_dir()
        self.save_card_image_map()

    def get_image_path(self, card_id: str) -> pathlib.Path:
        """Returns the image path for the given card id"""
        return self.image_dir.joinpath(self.card_image_map[card_id])

    def download_card_images(self, cards: Iterable[Card], force: bool = False):
        """Downloads the images for the given cards"""
        for card in cards:
            img_name = f"{card.id}.png"
            image_path = self.image_dir.joinpath(img_name)
            if not image_path.exists() or force:
                logger.info("downloading %s", card.id)
                if download_save_image(card.images.large, image_path):
                    self.card_image_map[card.id] = img_name


class CardManager(BaseCardManager):
    """Manages the card and set data for the Pokémon TCG"""

    def __init__(self, api_client: CardAPIClient | None = None):
        self.api_client = api_client or PokemonTCGSDKClient()
        self.card_path = get_pickle_dir("pokemon").joinpath("cards.pickle")
        self.set_path = get_pickle_dir("pokemon").joinpath("sets.pickle")
        self.set_card_path = get_pickle_dir("pokemon").joinpath("cards_by_set.pickle")
        self.card_data = self.get_data("cards")
        self.set_data = self.get_data("sets")
        self.set_card_map = self.get_set_card_map()

    def get_data(self, data_item: str, overwrite: bool = False) -> dict:
        """Gets the data for the given item, either from the pickle or from the API"""
        if data_item == "cards":
            path = self.card_path
            logger.info("getting cards")
            items = self.api_client.iter_cards
        elif data_item == "sets":
            path = self.set_path
            logger.info("getting sets")
            items = self.api_client.iter_sets
        else:
            raise ValueError(f"invalid item: {data_item}")
        if path.exists() and not overwrite:
            logger.info("loading %s", data_item)
            return load_pickle(path, default={})
        data = {}
        for item in items():
            data[item.id] = item
        logger.info("saving %s to %s", data_item, path)
        save_pickle(data, path)
        return data

    def get_set_card_map(self, overwrite: bool = False) -> dict[str, list[str]]:
        """Gets the set_card_map, either from the pickle or from the API"""
        if self.set_card_path.exists() and not overwrite:
            logger.info("loading cards_by_set")
            return load_pickle(self.set_card_path, default={})
        set_card_map = {}
        logger.info("computing cards_by_set")
        for card in self.card_data.values():
            if card.set.id not in set_card_map:
                set_card_map[card.set.id] = []
            set_card_map[card.set.id].append(card.id)
        logger.info("saving cards_by_set to %s", self.set_card_path)
        save_pickle(set_card_map, self.set_card_path)
        return set_card_map

    def refresh_data(self) -> None:
        """Refreshes the card and set data"""
        self.card_data = self.get_data("cards", True)
        self.set_data = self.get_data("sets", True)
        self.set_card_map = self.get_set_card_map(True)
