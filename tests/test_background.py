import pytest

from card_identifier.config import config
from card_identifier.image import background


def test_random_bg_image_missing_dir(tmp_path):
    """random_bg_image should raise when background dir missing or empty."""
    # Use a path that does not exist
    config.backgrounds_dir = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        background.random_bg_image((10, 10), {})
