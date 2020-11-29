import random
from typing import Tuple

from PIL import Image


def range_solid_colors() -> tuple:
    for r in range(-1, 256, 16):
        if r < 0: r = 0
        for g in range(-1, 256, 16):
            if g < 0: g = 0
            for b in range(-1, 256, 16):
                if b < 0: b = 0
                yield (r, g, b)


def range_placement(
        bg_size: Tuple[int, int],
        img_size: Tuple[int, int],
        slop: float,
        x_step: int = None,
        y_step: int = None,
        step_wobble: float = None) -> (Tuple[int, int], str):
    if x_step is None:
        x_step = int(bg_size[0] / 10)
    if y_step is None:
        y_step = int(bg_size[1] / 10)

    if img_size[0] * slop > bg_size[0]:
        range_x = 0
        x_zero = 0
    else:
        range_x = int(bg_size[0] - (img_size[0] * slop))
        x_zero = 0 - int(img_size[0] * slop)
    if img_size[1] * slop > bg_size[1]:
        range_y = 0
        y_zero = 0
    else:
        range_y = int(bg_size[1] - (img_size[1] * slop))
        y_zero = 0 - int(img_size[1] * slop)
    for x in range(x_zero, range_x + 1, x_step):
        for y in range(y_zero, range_y + 1, y_step):
            if step_wobble is not None:
                x_wobble = x_step * random.uniform(0,
                                                   step_wobble) * \
                           random.choice(
                    [1, -1])
                y_wobble = y_step * random.uniform(0,
                                                   step_wobble) * \
                           random.choice(
                    [1, -1])
                x += int(x_wobble)
                y += int(y_wobble)
            yield (x, y), f"pos-x{x}y{y}"


def mk_background(size: tuple, bg_color: tuple) -> (Image.Image, str):
    return (
        Image.new("RGB", size, bg_color),
        f"bg-r{bg_color[0]}g{bg_color[1]}b{bg_color[2]}")
