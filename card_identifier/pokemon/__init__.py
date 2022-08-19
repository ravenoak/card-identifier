import logging
import pathlib
import pickle
from typing import Dict, List, Union

from pokemontcgsdk import Card, Set

from card_identifier.data import get_image_dir, get_pickle_dir
from card_identifier.util import download_save_image

logger = logging.getLogger('card_identifier.pokemon')


class ImageManager:
    def __init__(self):
        self.pickle_dir = get_pickle_dir('pokemon')
        self.image_dir = get_image_dir('pokemon')
        self.card_image_file = self.pickle_dir.joinpath(
            "card_image_map.pickle")
        self.card_image_map = self.load_card_image_map()

    def load_card_image_map(self) -> Dict[str, pathlib.Path]:
        if self.card_image_file.exists():
            with open(self.card_image_file, "rb") as file:
                logger.info('opening card_image_map pickle')
                return pickle.load(file)
        else:
            logger.info('not loading card_image_map: missing')
            return {}

    def save_card_image_map(self):
        with open(self.card_image_file, "wb") as file:
            logger.info('saving card_image_map pickle')
            pickle.dump(self.card_image_map, file)

    def get_image_path(self, card_id: str) -> pathlib.Path:
        return self.card_image_map[card_id]

    def download_card_images(self, cards: List[Card], force: bool = False):
        for card in cards:
            img_name = pathlib.Path(card.id + '.png')
            image_path = self.image_dir.joinpath(img_name)
            if not image_path.exists() or force:
                logger.info(f'downloading {card.id}')
                if download_save_image(card.images.large, image_path):
                    self.card_image_map[card.id] = img_name


class CardManager:
    def __init__(self):
        self.card_path = get_pickle_dir('pokemon').joinpath("cards.pickle")
        self.set_path = get_pickle_dir('pokemon').joinpath("sets.pickle")
        self.set_card_path = get_pickle_dir('pokemon').joinpath(
            "cards_by_set.pickle")
        self.card_data = self.get_data('cards')
        self.set_data = self.get_data('sets')
        self.set_card_map = self.get_set_card_map()

    def get_data(self, item: str, overwrite=False) -> Dict:
        if item == 'cards':
            path = self.card_path
            items = Card.all
        elif item == 'sets':
            path = self.set_path
            items = Set.all
        else:
            raise ValueError(f'invalid item: {item}')
        if path.exists() and not overwrite:
            with open(path, "rb") as file:
                return pickle.load(file)
        else:
            data = dict()
            for item in items():
                data[item.id] = item
            with open(path, "wb") as file:
                pickle.dump(data, file)
            return data

    def get_set_card_map(self, overwrite=False):
        if self.set_card_path.exists() and not overwrite:
            with open(self.set_card_path, "rb") as file:
                return pickle.load(file)
        else:
            set_card_map = dict()
            for card_id, card in self.card_data.items():
                if card.set.id not in set_card_map:
                    set_card_map[card.set.id] = list()
                set_card_map[card.set.id].append(card.id)
            with open(self.set_card_path, "wb") as file:
                pickle.dump(set_card_map, file)
            return set_card_map

    def refresh_data(self):
        self.card_data = self.get_data('cards', True)
        self.set_data = self.get_data('sets', True)
        self.set_card_map = self.get_set_card_map(True)
