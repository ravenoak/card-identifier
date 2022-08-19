import logging
import multiprocessing as mp
import pathlib
import pickle
import random

import click

from card_identifier.data import get_dataset_dir, get_pickle_dir
from card_identifier.image import gen_random_dataset
from card_identifier import pokemon
from card_identifier.util import setup_logging

logger = logging.getLogger('card_identifier')


def create_random_training_images(num: int, id_filter: str = None):
    pickle_dir = get_pickle_dir('pokemon')
    dataset_dir = get_dataset_dir()
    random_state_pickle = pickle_dir.joinpath("random_state.pickle")
    if random_state_pickle.exists():
        with open(random_state_pickle, "rb") as file:
            logger.info('opening random_state pickle')
            random.setstate(pickle.load(file))
    else:
        logger.info('not loading random_state: missing')
    with open(pickle_dir.joinpath("card_image_map.pickle"), "rb") as file:
        logger.info('opening card_image_map pickle')
        id_image_map = pickle.load(file)
    work = []
    for img_id, path in id_image_map.items():
        if id_filter is None or img_id.startswith(id_filter):
            work.append(
                (img_id, pathlib.Path(path), pathlib.Path(dataset_dir), num)
            )
    with mp.Pool(processes=None) as pool:
        logger.info('starting gen_dataset in pool')
        pool.starmap(gen_random_dataset, work)


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    setup_logging(debug)


@cli.command()
@click.option('-r', '--refresh', default=False, is_flag=True)
@click.option('-f / ', '--force/--no-force', default=False)
@click.option('-i / ', '--images/--no-images', default=False)
@click.option('-t', '--card-type',
              type=click.Choice(['pokemon', ], case_sensitive=False),
              default='pokemon')
@click.pass_context
def card_data(ctx, card_type, images, force, refresh):
    logging.info('card-data')
    if card_type == 'pokemon':
        logger.info('Pokemon!')
        cm = pokemon.CardManager()
        if refresh:
            cm.refresh_data()
        if images:
            im = pokemon.ImageManager()
            im.download_card_images(cm.card_data.values(), force)


@cli.command()
@click.option('-f', '--str-filter', type=str, default=None)
@click.option('-n', '--number-of-images', type=int, default=100)
@click.pass_context
def create_dataset(ctx, number_of_images, str_filter):
    mp.set_start_method('spawn')
    create_random_training_images(number_of_images, str_filter)


@cli.command()
@click.option('-s', '--seed', type=int, default=None)
@click.option('-t', '--card-type',
              type=click.Choice(['pokemon', ], case_sensitive=False),
              default='pokemon')
@click.pass_context
def save_random_state(ctx, card_type, seed):
    pickle_dir = get_pickle_dir(card_type)
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
