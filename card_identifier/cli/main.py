import logging
import multiprocessing as mp
import pathlib
import pickle
import random

import click

from card_identifier.application import ImageService, CardService
from card_identifier.data import get_dataset_dir, get_pickle_dir, NAMESPACES
from card_identifier.dataset import DEFAULT_OUT_EXT, gen_random_dataset
from card_identifier.games import pokemon
from card_identifier.config import Settings
from card_identifier.util import setup_logging, load_random_state

logger = logging.getLogger("card_identifier.cli")


def create_random_training_images(num: int, card_type: str, id_filter: str = None):
    pickle_dir = get_pickle_dir(card_type)
    dataset_dir = get_dataset_dir(card_type)
    load_random_state(pickle_dir)
    with open(pickle_dir.joinpath("card_image_map.pickle"), "rb") as file:
        logger.debug("opening card_image_map pickle")
        id_image_map = pickle.load(file)
        # TODO: figure out how to sort id_image_map
    work = []
    logger.info("creating work queue")
    for card_id, path in id_image_map.items():
        data_path = f"data/images/originals/{card_type}/"
        original_path = pathlib.Path(data_path).joinpath(path)
        if not original_path.exists():
            logger.error(f"image {path} does not exist")
            continue
        if id_filter is None or card_id.startswith(id_filter):
            logger.debug(f"evaluating {card_id} for work")
            set_id = card_id.split("-")[0]
            save_path = pathlib.Path(dataset_dir).joinpath(
                f"{set_id}/{card_id}")
            if not save_path.exists():
                save_path.mkdir(parents=True)
                save_num = num
            else:
                save_num = num - len(list(save_path.glob(f"*.{DEFAULT_OUT_EXT}")))
                if save_num <= 0:
                    continue
            logger.info(f"adding {card_id} to work, generating {save_num} images")
            work.append(
                (pathlib.Path(data_path).joinpath(path),
                 save_path,
                 save_num)
            )
    with mp.Pool(processes=None) as pool:
        logger.info("starting gen_dataset in pool")
        pool.starmap(gen_random_dataset, work)


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj["settings"] = Settings()
    ctx.obj["settings"].debug = debug
    setup_logging(debug)


@cli.command()
@click.option("-r", "--refresh", default=False, is_flag=True)
@click.option("-f / ", "--force/--no-force", default=False)
@click.option("-i / ", "--images/--no-images", default=False)
@click.option("-t", "--card-type",
              type=click.Choice(NAMESPACES, case_sensitive=False),
              default="pokemon")
@click.pass_context
def card_data(ctx, card_type, images, force, refresh):
    """Manages the card data for the given card type"""
    logging.info("card-data")
    if card_type == "pokemon":
        logger.info("working with Pokémon data!")
        cm = pokemon.CardManager()
        if refresh:
            logging.info("refreshing card data")
            cm.refresh_data()
        if images:
            im = pokemon.ImageManager()
            logging.info("downloading card images")
            im.download_card_images(cm.card_data.values(), force)
            im.refresh_card_image_map()


@click.command()
@click.option('--force', is_flag=True, help='Force download of images even if they already exist.')
def download_images(force):
    """Download images for all cards."""
    card_service = CardService()
    image_service = ImageService()
    cards = card_service.get_all()
    image_service.download_card_images(cards, force=force)


@cli.command()
@click.option("-f", "--str-filter", type=str, default=None)
@click.option("-n", "--number-of-images", type=int, default=100)
@click.option("-t", "--card-type",
              type=click.Choice(NAMESPACES, case_sensitive=False),
              default="pokemon")
@click.pass_context
def create_dataset(ctx, card_type, number_of_images, str_filter):
    """Creates a random dataset of the given size for the given card type"""
    mp.set_start_method("spawn")
    create_random_training_images(number_of_images, card_type, str_filter)


@cli.command()
@click.option("-n", "--number-of-images", type=int, default=100)
@click.option("-t", "--card-type",
              type=click.Choice(NAMESPACES, case_sensitive=False),
              default="pokemon")
@click.pass_context
def trim_dataset(ctx, card_type, number_of_images):
    """Trims the dataset to the given number of images per card"""
    pickle_dir = get_pickle_dir(card_type)
    dataset_dir = get_dataset_dir(card_type)
    load_random_state(pickle_dir)
    for set_dir in dataset_dir.glob('*'):
        if set_dir.is_dir():
            for image_dir in set_dir.glob('*'):
                if image_dir.is_dir():
                    images = list(image_dir.glob(f'*.{DEFAULT_OUT_EXT}'))
                    if len(images) > number_of_images:
                        random.shuffle(images)
                        for image in images[number_of_images:]:
                            image.unlink()


@cli.command()
@click.option("-s", "--seed", type=int, default=None)
@click.option("-t", "--card-type",
              type=click.Choice(NAMESPACES, case_sensitive=False),
              default="pokemon")
@click.pass_context
def save_random_state(ctx, card_type, seed):
    """Saves the random state to a pickle file"""
    pickle_dir = get_pickle_dir(card_type)
    with open(pickle_dir.joinpath("random_state.pickle"), "wb") as file:
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()
        logger.info("saving random state")
        pickle.dump(random.getstate(), file)


def run():
    cli(obj={})


if __name__ == "__main__":
    run()
