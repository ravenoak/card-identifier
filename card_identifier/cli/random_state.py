import logging
import pickle
import random

import click

from card_identifier.data import get_pickle_dir, NAMESPACES

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
    with open(pickle_dir.joinpath("random_state.pickle"), "wb") as file:
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()
        logger.info("saving random state")
        pickle.dump(random.getstate(), file)
