from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class ImageMeta:
    """Metadata about a generated dataset image."""

    filename: str
    details: Dict[str, Any]
