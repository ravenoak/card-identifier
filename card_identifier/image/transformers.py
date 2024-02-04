import random
from typing import Tuple

import numpy as np
from PIL import Image
from PIL import ImageOps
from skimage.util import random_noise


def _find_coefficients(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])

    a = np.matrix(matrix, dtype=float)
    b = np.array(pb).reshape(8)

    res = np.dot(np.linalg.inv(a.T * a) * a.T, b)
    return np.array(res).reshape(8)


def _add_noise(image: Image.Image, **kwargs) -> Tuple[Image.Image, dict]:
    arr = np.array(image)
    arr = random_noise(arr, **kwargs)
    arr = np.array(255 * arr, dtype="uint8")
    meta = {
        "transformer": "noise",
        "method": "skimage.util.random_noise",
    }
    return Image.fromarray(arr), meta


def add_noise_salt_n_pepper(image: Image.Image, amount: float = 0.01) -> Tuple[Image.Image, dict]:
    img, meta = _add_noise(image, mode='s&p', amount=amount)
    meta["mode"] = "s&p"
    meta["amount"] = amount
    return img, meta


def random_resize(image: Image.Image, resize_percent: float = 0.3) -> Tuple[Image.Image, dict]:
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


def random_perspective_transform(img: Image.Image, wobble_percent: float = 0.2) -> Tuple[Image.Image, dict]:
    def wobble(xy, size):
        return xy + int((random.randint(int(0 - (wobble_percent * 100)), int(0 + (wobble_percent * 100))) / 100) * size)

    w, h = img.size
    x0: int = wobble(0, w)
    y0: int = wobble(0, h)

    x1: int = wobble(w, w)
    y1: int = wobble(0, h)

    x2: int = wobble(w, w)
    y2: int = wobble(h, h)

    x3: int = wobble(0, w)
    y3: int = wobble(h, h)

    # put image fully in frame
    adj_x = abs(min(x0, x1, x2, x3))
    adj_y = abs(min(y0, y1, y2, y3))
    pa: list[tuple[int, int]] = [(x0 + adj_x, y0 + adj_y), (x1 + adj_x, y1 + adj_y), (x2 + adj_x, y2 + adj_y),
                                 (x3 + adj_x, y3 + adj_y)]
    pb: list[tuple[int, int]] = [(0, 0), (w, 0), (w, h), (0, h)]
    coefficients = _find_coefficients(pa, pb)
    return (
        img.transform(
            (int(img.size[0] * (1 + wobble_percent)), int(img.size[1] * (1 + wobble_percent))),
            Image.PERSPECTIVE,
            data=coefficients,
            resample=Image.BICUBIC,
            fill=0
        ).resize((w, h)),
        {
            "transformer": "perspective",
            "pa": pa,
            "coefficients": coefficients,
            "method": "PIL.Image.Image.transform"
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
    return image, meta


def random_rotate(image: Image.Image) -> Tuple[Image.Image, dict]:
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


def random_random_transformer(img: Image.Image) -> Tuple[Image.Image, dict]:
    xformers = [
        random_autocontrast,
        random_posterize,
        random_solarize,
    ]
    xformer = random.choice(xformers)
    return xformer(img)
