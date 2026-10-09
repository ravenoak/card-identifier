from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

__version__ = "0.1.0"
__pypi_packagename__ = "collectable-card-identifier"


def _env_path(var: str, default: Path) -> Path:
    value = os.getenv(var)
    return Path(value) if value else default


@dataclass
class PathsConfig:
    """Configuration for key filesystem locations."""

    data_root: Path = field(
        default_factory=lambda: Path(os.getenv("CARDIDENT_DATA_ROOT", "data"))
    )
    backgrounds_dir: Path = field(init=False)
    images_dir: Path = field(init=False)
    datasets_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        self.backgrounds_dir = _env_path(
            "CARDIDENT_BACKGROUNDS_DIR", self.data_root / "backgrounds"
        )
        self.images_dir = _env_path(
            "CARDIDENT_IMAGES_DIR", self.data_root / "images" / "originals"
        )
        self.datasets_dir = _env_path(
            "CARDIDENT_DATASETS_DIR", self.data_root / "images" / "dataset"
        )


# Global configuration used by the rest of the package
config = PathsConfig()
