import logging

import click

from card_identifier.data import NAMESPACES
from card_identifier.dataset.generator import DatasetBuilder

logger = logging.getLogger(__name__)


def create_random_training_images(num: int, card_type: str, id_filter: str = None):
    """Build a work queue and generate the dataset."""
    builder = DatasetBuilder(card_type=card_type, num_images=num, id_filter=id_filter)
    builder.run()


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
    create_random_training_images(number_of_images, card_type, str_filter)
