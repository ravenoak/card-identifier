import logging

import click

from card_identifier.data import NAMESPACES
from card_identifier.dataset.generator import DatasetBuilder

logger = logging.getLogger(__name__)


def create_random_training_images(
    num: int, card_type: str, id_filter: str | None = None
) -> None:
    """Generate a dataset of random card images.

    Parameters
    ----------
    num:
        Number of images to create.
    card_type:
        Namespace of cards to sample from.
    id_filter:
        Restrict the random draw to card IDs containing this substring.

    Returns
    -------
    None
        The generated images are written to the dataset directory.

    Side Effects
    ------------
    Creates image files on disk via :class:`~card_identifier.dataset.generator.DatasetBuilder`.
    """

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
def create_dataset(
    ctx: click.Context, card_type: str, number_of_images: int, str_filter: str | None
) -> None:
    """CLI entry point for generating a random training set.

    Parameters
    ----------
    ctx:
        ``click`` context object.
    card_type:
        Namespace of cards to sample from.
    number_of_images:
        Total number of images to produce.
    str_filter:
        Optional substring filter used to limit the cards that may be drawn.

    Returns
    -------
    None
        Images are written to the dataset directory via
        :func:`create_random_training_images`.
    """

    create_random_training_images(number_of_images, card_type, str_filter)
