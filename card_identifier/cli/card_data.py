import logging

import click

from card_identifier.cards import pokemon
from card_identifier.data import NAMESPACES

logger = logging.getLogger(__name__)


@click.command()
@click.option("-r", "--refresh", default=False, is_flag=True)
@click.option("-f", "--force/--no-force", default=False)
@click.option("-i", "--images/--no-images", default=False)
@click.option(
    "-t",
    "--card-type",
    type=click.Choice(NAMESPACES, case_sensitive=False),
    default="pokemon",
)
@click.pass_context
def card_data(
    ctx: click.Context, card_type: str, images: bool, force: bool, refresh: bool
) -> None:
    """Manage metadata and images for a particular card namespace.

    Parameters
    ----------
    ctx:
        ``click`` context object.
    card_type:
        Namespace of cards to manage.
    images:
        Download card images when ``True``.
    force:
        Overwrite any existing image files when downloading.
    refresh:
        Refresh cached card metadata before processing.

    Returns
    -------
    None
        Card metadata and images are written to disk as a side effect.
    """
    logging.info("card-data")
    if card_type == "pokemon":
        logger.info("working with Pokémon data!")
        cm = pokemon.CardManager()
        if refresh:
            logging.info("refreshing card data")
            cm.refresh_data()
        if images:
            im = pokemon.ImageManager()
            logging.info("downloading card images")
            im.download_card_images(cm.card_data.values(), force)
            im.refresh_card_image_map()
