import multiprocessing

from card_identifier.dataset import gen_random_dataset
from card_identifier.storage import StorageConfig, driver_map


class ImageService:
    def __init__(self, image_repository):
        self.image_repository = image_repository

    def download_card_images(self, cards, force=False):
        for card in cards:
            if force or not self.image_repository.exists(card.image_url):
                self.image_repository.download(card.image_url)

    def generate_dataset(self, image_id, dataset_size, subject_noise=False):
        args = [(image_id, subject_noise) for _ in range(dataset_size)]

        with multiprocessing.Pool() as pool:
            pool.starmap(gen_random_dataset, args)


class CardService:
    def __init__(self, card_repository):
        self.card_repository = card_repository

    def get_all(self):
        return self.card_repository.get_all()

    def refresh_data(self):
        self.card_repository.refresh_data()


class ImageStorage:
    def __init__(self, config: StorageConfig):
        self.config = config
        self._driver = None

    @property
    def driver(self):
        if not self._driver:
            config_class, driver_class = driver_map.get(self.config.storage_type)
            if isinstance(self.config.settings, config_class):
                self._driver = driver_class(self.config.settings)
            else:
                raise ValueError("Unsupported storage type or invalid settings.")
        return self._driver