import logging
import pathlib
import pickle
from typing import Dict, List

from pokemontcgsdk import Card, Set

from card_identifier.data import get_image_dir, get_pickle_dir
from card_identifier.util import download_save_image

logger = logging.getLogger("card_identifier.pokemon")


def get_legal_sets():
    return set(
        (s.id for s in Set.where(q="legalities.standard:legal"))).union(
        set((s.id for s in Set.where(q="legalities.expanded:legal"))))


class ImageManager:
    """Manages the original images for the Pokémon TCG"""
    def __init__(self):
        self.pickle_dir = get_pickle_dir("pokemon")
        self.image_dir = get_image_dir("pokemon")
        self.card_image_file = self.pickle_dir.joinpath(
            "card_image_map.pickle")
        self.card_image_map = self.load_card_image_map()

    def scan_img_dir(self) -> Dict[str, str]:
        """Creates a map of card id to image path for all images in the image_dir"""
        card_image_map = {}
        for img in self.image_dir.glob("**/*.png"):
            card_image_map[img.stem] = img.name
        return card_image_map

    def load_card_image_map(self) -> Dict[str, pathlib.Path]:
        """Loads the card_image_map pickle if it exists, otherwise returns an empty dict"""
        if self.card_image_file.exists():
            with open(self.card_image_file, "rb") as file:
                logger.info("opening card_image_map pickle")
                return pickle.load(file)
        else:
            logger.info("not loading card_image_map: missing")
            return {}

    def save_card_image_map(self):
        """Saves the card_image_map pickle"""
        with open(self.card_image_file, "wb") as file:
            logger.info("saving card_image_map pickle")
            pickle.dump(self.card_image_map, file)

    def refresh_card_image_map(self):
        """Refreshes the card_image_map pickle"""
        self.card_image_map = self.scan_img_dir()
        self.save_card_image_map()

    def get_image_path(self, card_id: str) -> pathlib.Path:
        """Returns the image path for the given card id"""
        return self.card_image_map[card_id]

    def download_card_images(self, cards: List[Card], force: bool = False):
        """Downloads the images for the given cards"""
        for card in cards:
            img_name = pathlib.Path(card.id + ".png")
            image_path = self.image_dir.joinpath(img_name)
            if not image_path.exists() or force:
                logger.info(f"downloading {card.id}")
                if download_save_image(card.images.large, image_path):
                    self.card_image_map[card.id] = img_name


class CardManager:
    """Manages the card and set data for the Pokémon TCG"""
    def __init__(self):
        self.card_path = get_pickle_dir("pokemon").joinpath("cards.pickle")
        self.set_path = get_pickle_dir("pokemon").joinpath("sets.pickle")
        self.set_card_path = get_pickle_dir("pokemon").joinpath(
            "cards_by_set.pickle")
        self.card_data = self.get_data("cards")
        self.set_data = self.get_data("sets")
        self.set_card_map = self.get_set_card_map()

    def get_data(self, data_item: str, overwrite: bool = False) -> Dict:
        """Gets the data for the given item, either from the pickle or from the API"""
        if data_item == "cards":
            path = self.card_path
            logger.info("getting cards")
            items = Card.all
        elif data_item == "sets":
            path = self.set_path
            logger.info("getting sets")
            items = Set.all
        else:
            raise ValueError(f"invalid item: {data_item}")
        if path.exists() and not overwrite:
            logger.info(f"loading {data_item}")
            with open(path, "rb") as file:
                return pickle.load(file)
        else:
            data = dict()
            for item in items():
                data[item.id] = item
            logger.info(f"saving {data_item} to {path}")
            with open(path, "wb") as file:
                pickle.dump(data, file)
            return data

    def get_set_card_map(self, overwrite=False):
        """Gets the set_card_map, either from the pickle or from the API"""
        if self.set_card_path.exists() and not overwrite:
            logger.info("loading cards_by_set")
            with open(self.set_card_path, "rb") as file:
                return pickle.load(file)
        else:
            set_card_map = dict()
            logger.info("computing cards_by_set")
            for card_id, card in self.card_data.items():
                if card.set.id not in set_card_map:
                    set_card_map[card.set.id] = list()
                set_card_map[card.set.id].append(card.id)
            logger.info(f"saving cards_by_set to {self.set_card_path}")
            with open(self.set_card_path, "wb") as file:
                pickle.dump(set_card_map, file)
            return set_card_map

    def refresh_data(self):
        """Refreshes the card and set data"""
        self.card_data = self.get_data("cards", True)
        self.set_data = self.get_data("sets", True)
        self.set_card_map = self.get_set_card_map(True)
