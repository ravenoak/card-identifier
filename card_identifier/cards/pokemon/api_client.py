from __future__ import annotations

from typing import Iterable, Protocol

from pokemontcgsdk import Card, Set


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
        return Set.all()


__all__ = ["CardAPIClient", "PokemonTCGSDKClient"]
