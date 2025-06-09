from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

__version__ = "0.1.0"
__pypi_packagename__ = "collectable-card-identifier"


def _env_path(var: str) -> Path | None:
    value = os.getenv(var)
    return Path(value) if value else None


@dataclass
class PathsConfig:
    """Configuration for key filesystem locations."""

    data_root: Path = Path(os.getenv("CARDIDENT_DATA_ROOT", "data"))
    backgrounds_dir: Path | None = _env_path("CARDIDENT_BACKGROUNDS_DIR")
    images_dir: Path | None = _env_path("CARDIDENT_IMAGES_DIR")
    datasets_dir: Path | None = _env_path("CARDIDENT_DATASETS_DIR")

    def __post_init__(self) -> None:
        if self.backgrounds_dir is None:
            self.backgrounds_dir = self.data_root / "backgrounds"
        if self.images_dir is None:
            self.images_dir = self.data_root / "images" / "originals"
        if self.datasets_dir is None:
            self.datasets_dir = self.data_root / "images" / "dataset"


# Global configuration used by the rest of the package
config = PathsConfig()
