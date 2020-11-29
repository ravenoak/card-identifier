import pickle
from typing import List

import requests
from pokemontcgsdk import Card

from main import get_image_dir, get_pickle_dir


def download_cards() -> List[Card]:
    all_cards = Card.all()

    path = get_pickle_dir()

    with open(path.joinpath("card-all.pickle"), "wb") as file:
        pickle.dump(all_cards, file)

    return all_cards


def download_card_images(cards: List[Card], overwrite=False):
    image_dir = get_image_dir()
    id_image_map = {}

    for card in cards:
        path = image_dir.joinpath(
            ".".join([card.id, card.image_url.split(".")[-1]]))
        if not path.exists() or overwrite:
            image = requests.get(card.image_url, allow_redirects=True)
            print(f"Downloaded image: {card.image_url}")
            if image.ok:
                with open(path, "wb") as file:
                    file.write(image.content)
                print(f"File written: {path}")
                id_image_map[card.id] = path
            else:
                print(f"Error retrieving image: {card.image_url}")

    pickle_dir = get_pickle_dir()
    with open(pickle_dir.joinpath("id_image_map.pickle"), "wb") as file:
        pickle.dump(id_image_map, file)
