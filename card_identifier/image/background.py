import random
from typing import Tuple

from PIL import Image

from card_identifier.config import config

BACKGROUND_TYPES = [
    "random_solid_color",
    "random_bg_image",
]


def random_solid_color(size: tuple[int, int], meta) -> Image.Image:
    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    meta["bg_color"] = bg_color
    return Image.new("RGBA", size, bg_color)


def random_bg_image(size: tuple[int, int], meta) -> Image.Image:
    """Return a random background image resized to ``size``.

    Raises
    ------
    FileNotFoundError
        If ``config.backgrounds_dir`` does not exist or contains no images.
    """

    if not config.backgrounds_dir.exists():
        raise FileNotFoundError(
            f"backgrounds directory does not exist: {config.backgrounds_dir}"
        )

    images = [p for p in config.backgrounds_dir.glob("*") if p.is_file()]
    if not images:
        raise FileNotFoundError(
            f"no background images found in {config.backgrounds_dir}"
        )

    path = random.choice(images)
    with Image.open(path) as bg_image:
        meta["bg_image"] = bg_image.filename
        img = Image.new("RGBA", size)
        img.paste(bg_image.resize(size), (0, 0))
    return img


def random_placement(
    bg_size: Tuple[int, int], img_size: Tuple[int, int], limit: float
) -> (Tuple[int, int], dict):
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
        },
    )
