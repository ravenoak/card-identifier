import hashlib
import logging
import pathlib
import pickle
import random
from typing import Dict, Union

from PIL import Image

from card_identifier.cards.pokemon import get_legal_sets
from card_identifier.data import get_image_dir, get_dataset_dir
from card_identifier.image import transformers, background, func_map
from card_identifier.util import setup_logging

DEFAULT_WORKING_SIZE = (1024, 1024)
DEFAULT_OUT_SIZE = (224, 224)
DEFAULT_OUT_EXT = "png"

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
        if training_type == "all":
            logger.info("making symlinks for all cards")
        elif training_type == "legal":
            logger.info("making symlinks for legal cards")
            legal_sets = get_legal_sets()
        elif training_type == "sets":
            logger.info("making symlinks for cards in sets")
        else:
            raise ValueError(f"invalid training_type: {training_type}")


def gen_random_dataset(image_path: pathlib.Path, save_path: pathlib.Path, dataset_size: int, xform=False):
    """Generates a random dataset of the given size from the given image."""
    # TODO: Need to handle logging better in multiprocessing.
    setup_logging(False)
    if not image_path.exists() and image_path.is_file():
        logger.error(f"Image path does not exist or is not a file: {image_path}")
        return
    if not save_path.exists():
        raise ValueError(f"Save path does not exist: {save_path}")
    logger.info(f"Generating {dataset_size} images from {image_path}")
    src_image = Image.open(image_path)
    src_image = src_image.convert(mode="RGBA")
    for iteration in range(0, dataset_size):
        logger.debug(f"Generating image {image_path} {iteration} of {dataset_size}")
        meta = {"transform": xform}
        if xform and random.random() < 0.5:
            xform_image, xform_meta = transformers.random_random_transformer(src_image)
            meta.update(xform_meta)
        else:
            xform_image = src_image

        resized_img, resize_meta = transformers.random_resize(xform_image)
        meta.update(resize_meta)
        perspective_img, perspective_meta = transformers.random_perspective_transform(resized_img)
        meta.update(perspective_meta)
        rot_image, rot_meta = transformers.random_rotate(perspective_img)
        meta.update(rot_meta)
        bg_type = random.choice(background.BACKGROUND_TYPES)
        meta["bg_type"] = bg_type
        base_image = func_map[bg_type](DEFAULT_WORKING_SIZE, meta)
        pos, pos_meta = background.random_placement(base_image.size, rot_image.size, 0.75)
        meta.update(pos_meta)
        base_image.paste(rot_image, pos, rot_image.split()[3])
        base_image = base_image.convert(mode="RGB")
        image_hash = hashlib.sha256(base_image.tobytes()).hexdigest()
        filename = f"{image_hash}.{DEFAULT_OUT_EXT}"
        base_image.resize(DEFAULT_OUT_SIZE).save(open(save_path.joinpath(filename), "wb"), DEFAULT_OUT_EXT)
        # TODO: Figure out what to to with the meta data.
        logger.debug(f"Generated image with meta: {meta}")
