import abc
import pathlib
from typing import Dict


class IDatasetStorageManager(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'load_dataset')
                and callable(subclass.load_dataset)
                and hasattr(subclass, 'save_dataset')
                and callable(subclass.save_dataset)
                or NotImplemented)

    @abc.abstractmethod
    def load_dataset(self) -> Dict[str, pathlib.Path]:
        raise NotImplementedError

    @abc.abstractmethod
    def save_dataset(self):
        raise NotImplementedError
