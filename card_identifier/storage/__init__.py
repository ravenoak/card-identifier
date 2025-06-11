from typing import Tuple, Type

from pydantic import BaseModel, model_validator, ValidationError

from card_identifier.storage.filesystem import FileSystemConfig, FileSystemDriver

driver_map = {
    'filesystem': (FileSystemConfig, FileSystemDriver)
}


def get_available_drivers():
    return driver_map.keys()


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
