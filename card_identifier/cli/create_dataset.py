import logging
import multiprocessing as mp
import pickle

import click

from card_identifier.data import (
    get_dataset_dir,
    get_pickle_dir,
    get_image_dir,
    NAMESPACES,
)
from card_identifier.dataset.generator import DEFAULT_OUT_EXT, gen_random_dataset
from card_identifier.util import load_random_state

logger = logging.getLogger(__name__)


def create_random_training_images(num: int, card_type: str, id_filter: str = None):
    pickle_dir = get_pickle_dir(card_type)
    dataset_dir = get_dataset_dir(card_type)
    load_random_state(pickle_dir)
    with open(pickle_dir.joinpath("card_image_map.pickle"), "rb") as file:
        logger.debug("opening card_image_map pickle")
        id_image_map = pickle.load(file)
    image_dir = get_image_dir(card_type)
    work = []
    logger.info("creating work queue")
    for card_id, path in id_image_map.items():
        original_path = image_dir.joinpath(path)
        if not original_path.exists():
            logger.error(f"image {path} does not exist")
            continue
        if id_filter is None or card_id.startswith(id_filter):
            logger.debug(f"evaluating {card_id} for work")
            set_id = card_id.split("-")[0]
            save_path = dataset_dir.joinpath(f"{set_id}/{card_id}")
            if not save_path.exists():
                save_path.mkdir(parents=True)
                save_num = num
            else:
                save_num = num - len(list(save_path.glob(f"*.{DEFAULT_OUT_EXT}")))
                if save_num <= 0:
                    continue
            logger.info(
                f"adding {card_id} to work, generating {save_num} images"
            )
            work.append((image_dir.joinpath(path), save_path, save_num))
    with mp.Pool(processes=None) as pool:
        logger.info("starting gen_dataset in pool")
        pool.starmap(gen_random_dataset, work)


@click.command()
@click.option("-f", "--str-filter", type=str, default=None)
@click.option("-n", "--number-of-images", type=int, default=100)
@click.option(
    "-t",
    "--card-type",
    type=click.Choice(NAMESPACES, case_sensitive=False),
    default="pokemon",
)
@click.pass_context
def create_dataset(ctx, card_type, number_of_images, str_filter):
    """Creates a random dataset of the given size for the given card type."""
    mp.set_start_method("spawn")
    create_random_training_images(number_of_images, card_type, str_filter)
