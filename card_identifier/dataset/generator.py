import hashlib
import json
import logging
import multiprocessing as mp
import os
import pathlib
import pickle
import random
from typing import List, Optional, Tuple

from PIL import Image

from card_identifier.data import get_dataset_dir, get_image_dir, get_pickle_dir
from card_identifier.image import ImageMeta, background, func_map, transformers
from card_identifier.storage import load_random_state
from card_identifier.util import setup_logging

DEFAULT_WORKING_SIZE: Tuple[int, int] = (1024, 1024)
DEFAULT_OUT_SIZE: Tuple[int, int] = (224, 224)
DEFAULT_OUT_EXT = "png"

logger = logging.getLogger(__name__)


def gen_random_dataset(
    image_path: pathlib.Path,
    save_path: pathlib.Path,
    dataset_size: int,
    xform: bool = False,
) -> Optional[List[ImageMeta]]:
    """Generate a random dataset of the given size from the given image.

    Returns a list of :class:`ImageMeta` describing each generated image.  If
    ``image_path`` is missing, ``None`` is returned.
    """
    debug = os.getenv("CARDIDENT_DEBUG", "0") == "1"
    setup_logging(debug)
    if not image_path.exists() or not image_path.is_file():
        logger.error(f"Image path does not exist or is not a file: {image_path}")
        return
    if not save_path.exists():
        raise ValueError(f"Save path does not exist: {save_path}")
    logger.info(f"Generating {dataset_size} images from {image_path}")
    with Image.open(image_path) as img:
        src_image = img.convert(mode="RGBA")
    metas: List[ImageMeta] = []
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
        perspective_img, perspective_meta = transformers.random_perspective_transform(
            resized_img
        )
        meta.update(perspective_meta)
        rot_image, rot_meta = transformers.random_rotate(perspective_img)
        meta.update(rot_meta)
        bg_type = random.choice(background.BACKGROUND_TYPES)
        meta["bg_type"] = bg_type
        base_image = func_map[bg_type](DEFAULT_WORKING_SIZE, meta)
        pos, pos_meta = background.random_placement(
            base_image.size, rot_image.size, 0.75
        )
        meta.update(pos_meta)
        base_image.paste(rot_image, pos, rot_image.split()[3])
        base_image = base_image.convert(mode="RGB")
        image_hash = hashlib.sha256(base_image.tobytes()).hexdigest()
        filename = f"{image_hash}.{DEFAULT_OUT_EXT}"
        with open(save_path.joinpath(filename), "wb") as out_file:
            base_image.resize(DEFAULT_OUT_SIZE).save(out_file, DEFAULT_OUT_EXT)
        image_meta = ImageMeta(filename=filename, details=meta.copy())
        with open(save_path.joinpath(f"{image_hash}.json"), "w") as meta_file:
            json.dump(
                {"filename": image_meta.filename, "details": image_meta.details},
                meta_file,
            )
        metas.append(image_meta)
        logger.debug(f"Generated image with meta: {meta}")
    return metas


class DatasetBuilder:
    """Prepare work queues for dataset generation and execute them."""

    def __init__(self, card_type: str, num_images: int, id_filter: str | None = None):
        self.card_type = card_type
        self.num_images = num_images
        self.id_filter = id_filter

        self.pickle_dir = get_pickle_dir(card_type)
        self.image_dir = get_image_dir(card_type)
        self.dataset_dir = get_dataset_dir(card_type)

    def build_work(self) -> list[tuple[pathlib.Path, pathlib.Path, int]]:
        """Return a list of work items for dataset generation."""
        load_random_state(self.pickle_dir)
        work: list[tuple[pathlib.Path, pathlib.Path, int]] = []

        card_map = self.pickle_dir.joinpath("card_image_map.pickle")
        try:
            with open(card_map, "rb") as file:
                logger.debug("opening card_image_map pickle")
                id_image_map = pickle.load(file)
        except FileNotFoundError as exc:
            msg = f"card image map not found: {card_map}"
            logger.error(msg)
            raise FileNotFoundError(msg) from exc

        logger.info("creating work queue")
        for card_id, path in id_image_map.items():
            original_path = self.image_dir.joinpath(path)
            if not original_path.exists():
                logger.error(f"image {path} does not exist")
                continue
            if self.id_filter is None or card_id.startswith(self.id_filter):
                set_id = card_id.split("-")[0]
                save_path = self.dataset_dir.joinpath(f"{set_id}/{card_id}")
                if not save_path.exists():
                    save_path.mkdir(parents=True)
                    save_num = self.num_images
                else:
                    save_num = self.num_images - len(
                        list(save_path.glob(f"*.{DEFAULT_OUT_EXT}"))
                    )
                    if save_num <= 0:
                        continue
                logger.info(f"adding {card_id} to work, generating {save_num} images")
                work.append((original_path, save_path, save_num))

        return work

    def run(self) -> None:
        """Execute dataset generation using multiprocessing."""
        work = self.build_work()
        if not work:
            logger.warning("no work items generated")
            return
        debug = logging.getLogger().isEnabledFor(logging.DEBUG)
        os.environ["CARDIDENT_DEBUG"] = "1" if debug else "0"
        mp.set_start_method("spawn", force=True)
        with mp.Pool(processes=None) as pool:
            logger.info("starting gen_random_dataset in pool")
            pool.starmap(gen_random_dataset, work)
