import abc
import pathlib
from typing import Dict


class ICardManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod

class ICardImageManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'scan_img_dir')
                and callable(subclass.scan_img_dir)
                and hasattr(subclass, 'load_card_image_map')
                and callable(subclass.load_card_image_map)
                and hasattr(subclass, 'save_card_image_map')
                and callable(subclass.save_card_image_map)
                and hasattr(subclass, 'refresh_card_image_map')
                and callable(subclass.refresh_card_image_map)
                and hasattr(subclass, 'get_image_path')
                and callable(subclass.get_image_path)
                and hasattr(subclass, 'download_card_images')
                and callable(subclass.download_card_images)
                or NotImplemented)

    @abc.abstractmethod
    def load_card_image_map(self) -> Dict[str, pathlib.Path]:
        raise NotImplementedError

    @abc.abstractmethod
    def save_card_image_map(self):
        raise NotImplementedError

    @abc.abstractmethod
    def refresh_card_image_map(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_image_path(self, card_id: str) -> pathlib.Path:
        raise NotImplementedError

    @abc.abstractmethod
    def download_card_images(self, cards: list, force: bool = False):
        raise NotImplementedError
