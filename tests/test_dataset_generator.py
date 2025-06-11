import logging

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


def test_gen_random_dataset_no_fd_leak(tmp_path, monkeypatch):
    import os

    from PIL import Image

    image_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10), color=(255, 0, 0)).save(image_path)
    save_path = tmp_path / "out"
    save_path.mkdir()

    from card_identifier.config import config

    config.backgrounds_dir = tmp_path
    monkeypatch.setattr(
        generator.background, "BACKGROUND_TYPES", ["random_solid_color"]
    )
    monkeypatch.setattr(
        generator,
        "func_map",
        {"random_solid_color": generator.background.random_solid_color},
    )
    monkeypatch.setattr(
        generator.transformers,
        "random_perspective_transform",
        lambda img, wobble_percent=0.2: (img, {}),
    )

    before = len(os.listdir("/proc/self/fd"))
    result = generator.gen_random_dataset(image_path, save_path, 3)
    after = len(os.listdir("/proc/self/fd"))

    assert len(result) == 3
    assert before == after


def test_gen_random_dataset_with_transform_meta(tmp_path, monkeypatch):
    """gen_random_dataset should include transformer metadata when triggered."""
    from PIL import Image

    image_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10), color=(255, 0, 0)).save(image_path)
    save_path = tmp_path / "out"
    save_path.mkdir()

    from card_identifier.config import config

    config.backgrounds_dir = tmp_path
    monkeypatch.setattr(
        generator.background, "BACKGROUND_TYPES", ["random_solid_color"]
    )
    monkeypatch.setattr(
        generator,
        "func_map",
        {"random_solid_color": generator.background.random_solid_color},
    )
    monkeypatch.setattr(
        generator.transformers,
        "random_perspective_transform",
        lambda img, wobble_percent=0.2: (img, {}),
    )

    # Always trigger the random transformer
    monkeypatch.setattr(generator.random, "random", lambda: 0.0)
    monkeypatch.setattr(generator.transformers.random, "random", lambda: 0.0)
    monkeypatch.setattr(generator.transformers.random, "choice", lambda seq: seq[0])

    metas = generator.gen_random_dataset(image_path, save_path, 1, xform=True)

    assert len(metas) == 1
    meta = metas[0].details
    assert meta["transform"] is True
    assert "transformer" in meta
