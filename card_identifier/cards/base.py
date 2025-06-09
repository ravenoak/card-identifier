import abc
from typing import Dict


class BaseCardManager(abc.ABC):
    """Abstract base class for TCG card managers."""

    @abc.abstractmethod
    def get_data(self, data_item: str, overwrite: bool = False) -> Dict:
        """Return card or set data for *data_item*.

        Implementations should fetch the requested data from local
        storage or an API and may cache the result unless *overwrite*
        is ``True``.
        """

    @abc.abstractmethod
    def get_set_card_map(self, overwrite: bool = False) -> Dict:
        """Return a mapping of set ids to card ids."""

    @abc.abstractmethod
    def refresh_data(self) -> None:
        """Refresh cached data from the underlying source."""
