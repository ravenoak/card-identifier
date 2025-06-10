import logging

import click

from card_identifier.util import setup_logging
from .card_data import card_data
from .create_dataset import create_dataset
from .trim_dataset import trim_dataset
from .random_state import save_random_state

logger = logging.getLogger("card_identifier.cli")


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug
    setup_logging(debug)


cli.add_command(card_data)
cli.add_command(create_dataset)
cli.add_command(trim_dataset)
cli.add_command(save_random_state)


def run():
    cli(obj={})


if __name__ == "__main__":
    run()
