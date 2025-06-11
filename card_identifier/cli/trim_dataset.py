import logging
import random

import click

from card_identifier.data import NAMESPACES, get_dataset_dir, get_pickle_dir
from card_identifier.dataset.generator import DEFAULT_OUT_EXT
from card_identifier.storage import load_random_state

logger = logging.getLogger(__name__)


@click.command()
@click.option("-n", "--number-of-images", type=int, default=100)
@click.option(
    "-t",
    "--card-type",
    type=click.Choice(NAMESPACES, case_sensitive=False),
    default="pokemon",
)
@click.pass_context
def trim_dataset(ctx: click.Context, card_type: str, number_of_images: int) -> None:
    """Remove excess images from a dataset directory.

    Parameters
    ----------
    ctx:
        ``click`` context object.
    card_type:
        Namespace of cards to trim.
    number_of_images:
        Maximum number of images to keep per card.

    Returns
    -------
    None
        Excess images are removed from the dataset directory as a side effect.

    Side Effects
    ------------
    Deletes files from the dataset directory after loading the persisted
    random state to ensure deterministic trimming.
    """
    pickle_dir = get_pickle_dir(card_type)
    dataset_dir = get_dataset_dir(card_type)
    load_random_state(pickle_dir)
    for set_dir in dataset_dir.glob("*"):
        if set_dir.is_dir():
            for image_dir in set_dir.glob("*"):
                if image_dir.is_dir():
                    images = list(image_dir.glob(f"*.{DEFAULT_OUT_EXT}"))
                    if len(images) > number_of_images:
                        random.shuffle(images)
                        for image in images[number_of_images:]:
                            image.unlink()
