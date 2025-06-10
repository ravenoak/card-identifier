import logging
import pathlib
import pickle
import shutil
from typing import Dict, Union

from card_identifier.cards.pokemon import get_legal_sets
from card_identifier.data import get_image_dir, get_dataset_dir
from .generator import (
    DEFAULT_WORKING_SIZE,
    DEFAULT_OUT_SIZE,
    DEFAULT_OUT_EXT,
)

logger = logging.getLogger("card_identifier.dataset")


class DatasetManager:
    """Manages the image dataset for training the model on the specified TCG"""
    CARD_IMAGE_MAP = "card_image_map.pickle"

    def __init__(self, namespace: str):
        self.working_size = DEFAULT_WORKING_SIZE
        self.out_size = DEFAULT_OUT_SIZE
        self.out_ext = DEFAULT_OUT_EXT
        self.namespace = namespace
        self.image_dir = get_image_dir(namespace)
        self.dataset_dir = get_dataset_dir(namespace)
        self.card_dataset_map = self.load_card_dataset_map()
        self.num_img_desired = 100

    def load_card_dataset_map(self) -> Dict[str, pathlib.Path]:
        """Loads the card_dataset_map pickle if it exists, otherwise returns an empty dict"""
        if self.dataset_dir.joinpath(self.CARD_IMAGE_MAP).exists():
            with open(self.dataset_dir.joinpath(self.CARD_IMAGE_MAP), "rb") as file:
                return pickle.load(file)
        else:
            return {}

    def save_card_dataset_map(self):
        """Saves the card_dataset_map pickle"""
        with open(self.dataset_dir.joinpath(self.CARD_IMAGE_MAP), "wb") as file:
            pickle.dump(self.card_dataset_map, file)

    def scan_dataset_dir(self) -> dict[str, dict[str, Union[int, list]]]:
        """Creates a map of card id to image path for all images in the dataset_dir"""
        card_dataset_map = {}
        for img in self.dataset_dir.glob("**/*.png"):
            _id = img.parts[5]
            if not card_dataset_map.get(_id):
                card_dataset_map[_id] = {"num_img": 0, "img_paths": []}
            card_dataset_map[_id]["img_paths"].append(pathlib.Path(img))
            card_dataset_map[_id]["num_img"] += 1
        return card_dataset_map

    def mk_symlinks(self, training_type: str = "all"):
        """Create a symlink tree inside ``dataset_dir`` for training.

        The generated directory structure is ``dataset_dir/symlinks/<mode>`` and
        contains symlinks back to the real images organised by card id.  The
        ``mode`` can be one of ``"all"`` (every card), ``"legal"`` (only cards
        from legal sets) or ``"sets"`` (grouped by set then card).
        """

        if training_type not in {"all", "legal", "sets"}:
            raise ValueError(f"invalid training_type: {training_type}")

        if training_type == "legal":
            logger.info("making symlinks for legal cards")
            allowed_sets = get_legal_sets()
        else:
            allowed_sets = None
            if training_type == "all":
                logger.info("making symlinks for all cards")
            else:
                logger.info("making symlinks for cards in sets")

        base = self.dataset_dir.joinpath("symlinks", training_type)
        if base.exists():
            shutil.rmtree(base)
        base.mkdir(parents=True, exist_ok=True)

        for set_dir in self.dataset_dir.glob("*"):
            if not set_dir.is_dir():
                continue
            set_id = set_dir.name
            if allowed_sets is not None and set_id not in allowed_sets:
                continue
            for card_dir in set_dir.glob("*"):
                if not card_dir.is_dir():
                    logger.error(f"missing card directory: {card_dir}")
                    continue
                card_id = card_dir.name
                if training_type == "sets":
                    dest_dir = base.joinpath(set_id, card_id)
                else:
                    dest_dir = base.joinpath(card_id)
                dest_dir.mkdir(parents=True, exist_ok=True)
                for img in card_dir.glob(f"*.{self.out_ext}"):
                    if not img.exists():
                        logger.error(f"missing image file: {img}")
                        continue
                    link = dest_dir.joinpath(img.name)
                    if link.exists() or link.is_symlink():
                        link.unlink()
                    try:
                        link.symlink_to(img.resolve())
                    except FileNotFoundError:
                        logger.error(f"unable to symlink missing file: {img}")
