import logging
import random

import click

from card_identifier.data import get_pickle_dir, NAMESPACES
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
    """Saves the random state to a pickle file."""
    pickle_dir = get_pickle_dir(card_type)
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()
    logger.info("saving random state")
    save_state(pickle_dir)
