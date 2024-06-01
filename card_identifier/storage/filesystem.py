__all__ = ["FileSystemConfig", "FileSystemDriver"]

from pydantic import BaseModel


class FileSystemConfig(BaseModel):
    path: str = "/default/path"


class FileSystemDriver:
    def __init__(self, config: FileSystemConfig):
        self.config = config
