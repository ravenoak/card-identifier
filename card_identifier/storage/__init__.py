from pydantic import BaseModel, model_validator, ValidationError

from card_identifier.storage.filesystem import FileSystemConfig, FileSystemDriver

available_storage_types = ['filesystem']


class StorageConfig(BaseModel):
    storage_type: str
    settings: FileSystemConfig  # Union[S3Config, FileSystemConfig]

    @model_validator(mode='before')
    def validate_storage(cls, values):
        type_ = values.get('storage_type')
        settings = values.get('settings', {})
        config_class = {
            'filesystem': FileSystemConfig
        }.get(type_)

        if not config_class:
            raise ValueError(f"Unknown storage type: {type_}")

        try:
            values['settings'] = config_class(**settings)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration for {type_}: {e}")

        return values


class ImageStorage:
    driver_map = {
        'filesystem': (FileSystemConfig, FileSystemDriver)
    }

    def __init__(self, config: StorageConfig):
        self.config = config
        self._driver = None

    @property
    def driver(self):
        if not self._driver:
            config_class, driver_class = self.driver_map.get(self.config.storage_type)
            if isinstance(self.config.settings, config_class):
                self._driver = driver_class(self.config.settings)
            else:
                raise ValueError("Unsupported storage type or invalid settings.")
        return self._driver
