from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class Card:
    id: str
    name: str
    image_url: str


@dataclass
class Set:
    id: str
    name: str
    series: str
    total_cards: int
    release_date: str


class CardRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> List[Card]:
        pass

    @abstractmethod
    def get_cards_from_sets(self, set_ids: List[str]) -> List[Card]:
        pass


class SetRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> List[Set]:
        pass

    @abstractmethod
    def get_legal_sets(self) -> List[Set]:
        pass


class ImageManagerInterface(ABC):
    @abstractmethod
    def download_card_images(self, cards: List[Card], force: bool = False):
        pass
