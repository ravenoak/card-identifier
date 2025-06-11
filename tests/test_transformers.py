import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import math

from PIL import Image

from card_identifier.image import transformers

IMAGE_SIZE = (100, 50)


def create_image():
    return Image.new("RGB", IMAGE_SIZE, color=(255, 0, 0))


def test_random_resize_size_and_meta():
    img = create_image()
    resized, meta = transformers.random_resize(img, resize_percent=0.3)
    expected_size = (
        int(img.size[0] * meta["resize"]),
        int(img.size[1] * meta["resize"]),
    )
    assert resized.size == expected_size
    assert meta["transformer"] == "fuzzy_resize"
    assert meta["method"] == "PIL.Image.Image.resize"
    assert 0.7 <= meta["resize"] <= 1.3


def test_random_perspective_transform_size_and_meta():
    img = create_image()
    transformed, meta = transformers.random_perspective_transform(
        img, wobble_percent=0.2
    )
    assert transformed.size == img.size
    assert meta["transformer"] == "perspective"
    assert meta["method"] == "PIL.Image.Image.transform"
    assert isinstance(meta["pa"], list) and len(meta["pa"]) == 4
    assert len(meta["coefficients"]) == 8


def test_random_rotate_size_and_meta():
    img = create_image()
    rotated, meta = transformers.random_rotate(img)
    deg = meta["degrees"]
    assert 0 <= deg < 360
    assert meta["transformer"] == "rotate"

    w, h = img.size
    angle = math.radians(deg)
    expected_w = math.ceil(abs(w * math.cos(angle)) + abs(h * math.sin(angle)))
    expected_h = math.ceil(abs(h * math.cos(angle)) + abs(w * math.sin(angle)))
    assert abs(rotated.size[0] - expected_w) <= 1
    assert abs(rotated.size[1] - expected_h) <= 1


def test_random_autocontrast_size_and_meta():
    img = create_image()
    out, meta = transformers.random_autocontrast(img)
    assert out.size == img.size
    assert meta["transformer"] == "autocontrast"
    assert 0 <= meta["cutoff"] <= 40
    assert meta["method"] == "PIL.ImageOps.autocontrast"


def test_random_posterize_size_and_meta():
    img = create_image()
    out, meta = transformers.random_posterize(img)
    assert out.size == img.size
    assert meta["transformer"] == "posterize"
    assert 1 <= meta["bits"] <= 8
    assert meta["method"] == "PIL.ImageOps.posterize"


def test_random_solarize_size_and_meta():
    img = create_image()
    out, meta = transformers.random_solarize(img)
    assert out.size == img.size
    assert meta["transformer"] == "solarize"
    assert 1 <= meta["threshold"] <= 128
    assert meta["method"] == "PIL.ImageOps.solarize"
