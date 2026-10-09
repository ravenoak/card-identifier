from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from pokemontcgsdk import Card
from pokemontcgsdk.legality import Legality
from pokemontcgsdk.querybuilder import QueryBuilder
from pokemontcgsdk.setimage import SetImage


@dataclass
class PokemonSet:
    """``pokemontcgsdk.Set`` with ``printedTotal`` optional, since the API
    omits it for new sets and the SDK class then fails to parse them."""

    RESOURCE = "sets"

    id: str
    images: SetImage
    legalities: Legality
    name: str
    printedTotal: int | None
    ptcgoCode: str | None
    releaseDate: str
    series: str
    total: int
    updatedAt: str


class CardAPIClient(Protocol):
    """Interface for retrieving card and set data."""

    def iter_cards(self) -> Iterable:
        """Return an iterable of card objects."""
        ...

    def iter_sets(self) -> Iterable:
        """Return an iterable of set objects."""
        ...


class PokemonTCGSDKClient:
    """Implementation of :class:`CardAPIClient` using ``pokemontcgsdk``."""

    def iter_cards(self) -> Iterable:
        return Card.all()

    def iter_sets(self) -> Iterable:
        return QueryBuilder(PokemonSet).all()


__all__ = ["CardAPIClient", "PokemonTCGSDKClient"]
