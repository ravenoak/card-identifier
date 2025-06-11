import pytest

from card_identifier.config import config
from card_identifier.image import background


def test_random_bg_image_missing_dir(tmp_path):
    """random_bg_image should raise when background dir missing or empty."""
    # Use a path that does not exist
    config.backgrounds_dir = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        background.random_bg_image((10, 10), {})


def test_random_bg_image_no_fd_leak(tmp_path):
    """random_bg_image should not leak file descriptors."""
    import os

    from PIL import Image

    config.backgrounds_dir = tmp_path
    for i in range(3):
        Image.new("RGB", (10, 10), color=(i, i, i)).save(tmp_path / f"{i}.png")

    before = len(os.listdir("/proc/self/fd"))
    meta = {}
    img = background.random_bg_image((5, 5), meta)
    after = len(os.listdir("/proc/self/fd"))

    assert img.size == (5, 5)
    assert "bg_image" in meta
    assert before == after
