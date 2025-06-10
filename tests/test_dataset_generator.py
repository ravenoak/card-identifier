import logging
from pathlib import Path

import pytest

from card_identifier.dataset import generator


def test_gen_random_dataset_invalid_image_path(tmp_path, caplog):
    image_path = tmp_path / "missing.png"
    save_path = tmp_path / "out"
    save_path.mkdir()
    caplog.set_level(logging.ERROR)
    result = generator.gen_random_dataset(image_path, save_path, 1)
    assert result is None
    assert any(
        "does not exist or is not a file" in record.message for record in caplog.records
    )

def test_gen_random_dataset_invalid_save_path(tmp_path):
    image = tmp_path / "img.png"
    image.write_bytes(b"fake")
    save_path = tmp_path / "no_dir" / "sub"
    with pytest.raises(ValueError):
        generator.gen_random_dataset(image, save_path, 1)
