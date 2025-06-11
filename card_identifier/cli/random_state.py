import logging
import random

import click

from card_identifier.data import NAMESPACES, get_pickle_dir
from card_identifier.storage import save_random_state as save_state

logger = logging.getLogger(__name__)


@click.command(name="save-random-state")
@click.option("-s", "--seed", type=int, default=None)
@click.option(
    "-t",
    "--card-type",
    type=click.Choice(NAMESPACES, case_sensitive=False),
    default="pokemon",
)
@click.pass_context
def save_random_state(ctx, card_type, seed):
    """Persist Python's RNG state for reproducible dataset generation.

    Args:
        ctx (click.Context): CLI context.
        card_type (str): Namespace of cards associated with the state.
        seed (int | None): Seed to initialize ``random`` before saving.
    """
    pickle_dir = get_pickle_dir(card_type)
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()
    logger.info("saving random state")
    save_state(pickle_dir)
