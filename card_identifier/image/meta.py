from dataclasses import dataclass
from typing import Any


@dataclass
class ImageMeta:
    """Metadata about a generated dataset image."""

    filename: str
    details: dict[str, Any]
