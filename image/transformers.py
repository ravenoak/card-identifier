from typing import Tuple

from PIL.Image import Image
from PIL import ImageOps


def range_rotate(img: Image, bg_color: Tuple[int, int, int]) -> Tuple[Image, str]:
    # 15 positions
    for deg in range(0, 360, 24):
        yield img.rotate(deg, expand=True, fillcolor=bg_color), f"rotate-{deg}"

def range_autocontrast(img: Image) -> Tuple[Image, str]:
    # 5 positions
    for cutoff in range(0, 41, 10):
        yield ImageOps.autocontrast(img, cutoff), f"autocontrast-{cutoff}"

def range_posterize(img: Image) -> Tuple[Image, str]:
    # 8 positions
    for bits in range(1, 9):
        yield ImageOps.posterize(img, bits), f"posterize-{bits}"

def range_solarize(img: Image) -> Tuple[Image, str]:
    # 8 positions
    for threshold in range(16, 129, 16):
        yield ImageOps.solarize(img, threshold), f"solarize-{threshold}"

def range_transformers(img: Image, label: str) -> Tuple[Image, str]:
    xformers = [
        range_autocontrast,
        range_posterize,
        range_solarize,
    ]

    for xformer in xformers:
        for ximg, xlable in xformer(img):
            yield ximg, f"{label}-{xlable}"
