import random
from typing import Tuple

import numpy as np
from PIL import Image
from PIL import ImageOps
from skimage.util import random_noise


def _add_noise(image: Image.Image, **kwargs) -> Tuple[
    Image.Image, dict]:
    arr = np.array(image)
    arr = random_noise(arr, **kwargs)
    arr = np.array(255 * arr, dtype='uint8')
    meta = {
        "transformer": "noise",
        "method": "skimage.util.random_noise",
    }
    return (Image.fromarray(arr), meta)


def add_noise_salt_n_pepper(image: Image.Image, amount: float = 0.01) -> Tuple[
    Image.Image, dict]:
    img, meta = _add_noise(image, mode='s&p', amount=amount)
    meta["mode"] = "s&p"
    meta["amount"] = amount
    return (img, meta)


def random_resize(image: Image.Image, resize_percent: float = 0.3) -> Tuple[
    Image.Image, dict]:
    resize = random.randint(int(100 - (resize_percent * 100)),
                            int(100 + (resize_percent * 100))) / 100
    x = int(image.size[0] * resize)
    y = int(image.size[1] * resize)
    return (
        image.resize((x, y)),
        {
            "transformer": "fuzzy_resize",
            "resize": resize,
            "method": "PIL.Image.Image.resize",
        }
    )


def random_add_noise(image: Image.Image) -> Tuple[Image.Image, dict]:
    f = [
        "salt_n_pepper",
    ]

    noise = random.choice(f)
    if noise == "salt_n_pepper":
        amount = random.uniform(0.001, 0.01)
        image, meta = add_noise_salt_n_pepper(image, amount=amount)
    else:
        raise RuntimeError
    return (
        image, meta
    )


def random_rotate(image: Image.Image) -> Tuple[
    Image.Image, dict]:
    deg = random.randint(0, 359)
    return (
        image.rotate(deg, expand=True),
        {
            "transformer": "rotate",
            "degrees": deg,
        },
    )


def random_autocontrast(img: Image.Image) -> Tuple[Image.Image, dict]:
    cutoff = random.randint(0, 40)
    return (
        ImageOps.autocontrast(img, cutoff),
        {
            "transformer": "autocontrast",
            "cutoff": cutoff,
            "method": "PIL.ImageOps.autocontrast"
        }
    )


def random_posterize(img: Image.Image) -> Tuple[Image.Image, dict]:
    bits = random.randint(1, 8)
    return (
        ImageOps.posterize(img, bits),
        {
            "transformer": "posterize",
            "bits": bits,
            "method": "PIL.ImageOps.posterize"
        }
    )


def random_solarize(img: Image.Image) -> Tuple[Image.Image, dict]:
    threshold = random.randint(1, 128)
    return (
        ImageOps.solarize(img, threshold),
        {
            "transformer": "solarize",
            "threshold": threshold,
            "method": "PIL.ImageOps.solarize"
        }
    )


def random_random_transformer(img: Image.Image) -> Tuple[
    Image.Image, dict]:
    xformers = [
        random_autocontrast,
        random_posterize,
        random_solarize,
    ]
    xformer = random.choice(xformers)
    return xformer(img)
