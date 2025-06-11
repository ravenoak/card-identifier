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
def save_random_state(ctx: click.Context, card_type: str, seed: int | None) -> None:
    """Persist Python's RNG state for reproducible dataset generation.

    Parameters
    ----------
    ctx:
        ``click`` context object.
    card_type:
        Namespace of cards associated with the saved state.
    seed:
        Seed used to initialize :mod:`random` before persisting the state.  If
        ``None`` a random seed is chosen.

    Returns
    -------
    None
        The RNG state is written to ``pickle_dir/random_state.pkl``.

    Side Effects
    ------------
    Sets the global ``random`` module state and writes it to disk.
    """
    pickle_dir = get_pickle_dir(card_type)
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()
    logger.info("saving random state")
    save_state(pickle_dir)
