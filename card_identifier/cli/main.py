import logging
import multiprocessing as mp
import pathlib
import pickle
import random

import click

from card_identifier.data import get_dataset_dir, get_pickle_dir
from card_identifier.image import gen_random_dataset
from card_identifier import pokemon

logger = logging.getLogger('card_identifier')


def create_random_training_images(num: int, filter: str = None):
    pickle_dir = get_pickle_dir()
    dataset_dir = get_dataset_dir()
    random_state_pickle = pickle_dir.joinpath("random_state.pickle")
    if random_state_pickle.exists():
        with open(random_state_pickle, "rb") as file:
            logger.info('opening random_state pickle')
            random.setstate(pickle.load(file))
    else:
        logger.info('not loading random_state: missing')
    with open(pickle_dir.joinpath("id_image_map.pickle"), "rb") as file:
        logger.info('opening id_image_map pickle')
        id_image_map = pickle.load(file)
    work = []
    for id, path in id_image_map.items():
        if filter is None or id.startswith(filter):
            work.append(
                (id, pathlib.Path(path), pathlib.Path(dataset_dir), num)
            )
    with mp.Pool(processes=None) as pool:
        logger.info('starting gen_dataset in pool')
        pool.starmap(gen_random_dataset, work)


def setup_logging(debug: bool = False):
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=level,
    )


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    setup_logging(debug)


@cli.command()
@click.option('-f / ', '--force/--no-force', default=False)
@click.option('-i / ', '--images/--no-images', default=False)
@click.option('-t', '--card-type',
              type=click.Choice(['pokemon', ], case_sensitive=False),
              default='pokemon')
@click.pass_context
def card_data(ctx, card_type, images, force):
    logging.info('card-data')
    if card_type == 'pokemon':
        logger.info('Pokemon!')
        data = pokemon.get_card_data()
        if images:
            pokemon.download_card_images(data, force)


@cli.command()
@click.option('-f', '--filter', type=str, default=None)
@click.option('-n', '--number-of-images', type=int, default=100)
@click.pass_context
def create_dataset(ctx, number_of_images, filter):
    mp.set_start_method('spawn')
    create_random_training_images(number_of_images, filter)


@cli.command()
@click.option('-s', '--seed', type=int, default=None)
@click.pass_context
def save_random_state(ctx, seed):
    pickle_dir = get_pickle_dir()
    with open(pickle_dir.joinpath("random_state.pickle"), "wb") as file:
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()
        logger.info('saving random state')
        pickle.dump(random.getstate(), file)


def run():
    cli(obj={})


if __name__ == '__main__':
    run()
