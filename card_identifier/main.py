import multiprocessing as mp
import pathlib
import pickle

import click

from card_identifier.data import get_dataset_dir, get_pickle_dir
from card_identifier.image import gen_dataset
from card_identifier import pokemon


def create_training_images(save_percent: float = 0.01):
    mp.set_start_method('spawn')
    pickle_dir = get_pickle_dir()
    dataset_dir = get_dataset_dir()
    with open(pickle_dir.joinpath("id_image_map.pickle"), "rb") as file:
        id_image_map = pickle.load(file)
    work = []
    for id, path in id_image_map.items():
        if id.startswith('base1-'):
            work.append((id, pathlib.Path(path), pathlib.Path(dataset_dir),
                         save_percent))
    with mp.Pool(processes=None) as pool:
        pool.starmap(gen_dataset, work)


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj['DEBUG'] = debug


@cli.command()
@click.option('-f / ', '--force/--no-force', default=False)
@click.option('-t', '--card-type',
              type=click.Choice(['pokemon', ], case_sensitive=False),
              default='pokemon')
@click.pass_context
def card_data(ctx, card_type, force):
    click.echo('Debug is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))
    if card_type == 'pokemon':
        data = pokemon.download_cards()
        pokemon.download_card_images(data, force)


@cli.command()
@click.option('-s', '--save-percent', type=float, default=0.00001)
@click.pass_context
def images(ctx, save_percent):
    click.echo('Debug is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))
    create_training_images(save_percent)


if __name__ == '__main__':
    cli(obj={})
