import random
from typing import Tuple

from PIL import Image


def random_solid_color() -> Tuple[int, int, int]:
    return (random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))


def random_placement(bg_size: Tuple[int, int],
                     img_size: Tuple[int, int],
                     limit: float) -> (Tuple[int, int], dict):
    x_start = 0 - int(img_size[0] * (1 - limit))
    x_end = int(bg_size[0] - img_size[0] + (img_size[0] * (1 - limit)))
    y_start = 0 - int(img_size[1] * (1 - limit))
    y_end = int(bg_size[1] - img_size[1] + (img_size[1] * (1 - limit)))
    x = random.randint(x_start, x_end)
    y = random.randint(y_start, y_end)
    return (
        (x, y),
        {
            "position_x": x,
            "position_y": y,
        }
    )
