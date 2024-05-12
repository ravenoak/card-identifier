import abc
import random
from typing import Tuple
import pathlib

import numpy as np
from PIL import Image
from PIL import ImageOps
from skimage.util import random_noise


class ImageTransformationInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'apply_transformation') and
                callable(subclass.apply_transformation) and
                hasattr(subclass, 'update_metadata') and
                callable(subclass.update_metadata) or
                NotImplemented)

    @abc.abstractmethod
    def apply_transformation(self, image: Image.Image) -> Image.Image:
        raise NotImplementedError

    @abc.abstractmethod
    def update_metadata(self, metadata: dict) -> dict:
        raise NotImplementedError


class AddNoiseSaltNPepperTransformation(ImageTransformationInterface):
    """Adds salt and pepper noise to an image.

    A good method for randomness: random.uniform(0.001, 0.01)"""

    def __init__(self, amount: float = 0.01):
        self.amount = amount

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        arr = np.array(image)
        arr = random_noise(arr, mode='s&p', amount=self.amount)
        arr = np.array(255 * arr, dtype="uint8")
        return Image.fromarray(arr)

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "noise",
             "method": "skimage.util.random_noise",
             "parameters": {"mode": "s&p", "amount": self.amount}})
        return metadata


class PercentResizeTransformation(ImageTransformationInterface):
    def __init__(self, percent: float):
        self.percent = percent

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        return image.resize((int(image.size[0] * self.percent), int(image.size[1] * self.percent)))

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "resize",
             "method": "PIL.Image.Image.resize",
             "parameters": {"percent": self.percent}})
        return metadata


class RandomPercentResizeTransformation(PercentResizeTransformation):
    def __init__(self, lower_bound: float, upper_bound: float):
        super().__init__(
            random.randint(
                int(100 - (lower_bound * 100)),
                int(100 + (upper_bound * 100))
            ) / 100)


class PerspectiveTransformation(ImageTransformationInterface):
    def __init__(self, coefficients, method=Image.PERSPECTIVE, resample=Image.BICUBIC, fill=0, fillcolor=None):
        self.coefficients = coefficients
        self.method = method
        self.resample = resample
        self.fill = fill
        self.fillcolor = fillcolor

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        return image.transform(
            image.size,
            self.method,
            data=self.coefficients,
            resample=self.resample,
            fill=self.fill,
            fillcolor=None
        )

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "perspective",
             "method": "PIL.Image.Image.transform",
             "parameters": {"coefficients": self.coefficients,
                            "method": self.method,
                            "resample": self.resample,
                            "fill": self.fill,
                            "fillcolor": self.fillcolor}})
        return metadata


class WobblePerspectiveTransformation(PerspectiveTransformation):
    def __init__(self, image_size: Tuple[int, int], wobble_percent: float = 0.2):
        self.wobble_percent = wobble_percent

        self.pa, self.pb = self._make_perspective_shift(image_size)
        self._find_coefficients()
        super().__init__(
            self.coefficients,
            method=Image.PERSPECTIVE,
            resample=Image.BICUBIC,
            fill=0,
            fillcolor=None
        )

    def _find_coefficients(self):
        matrix = []
        for p1, p2 in zip(self.pa, self.pb):
            matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
            matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])

        a = np.matrix(matrix, dtype=float)
        b = np.array(self.pb).reshape(8)

        res = np.dot(np.linalg.inv(a.T * a) * a.T, b)
        self.coefficients = np.array(res).reshape(8)

    def _wobble(self, xy: int, size: int):
        return xy + int(
            (random.randint(int(0 - (self.wobble_percent * 100)), int(0 + (self.wobble_percent * 100))) / 100) * size)

    def _make_perspective_shift(self, image_size: Tuple[int, int]):
        w, h = image_size
        x0: int = self._wobble(0, w)
        y0: int = self._wobble(0, h)

        x1: int = self._wobble(w, w)
        y1: int = self._wobble(0, h)

        x2: int = self._wobble(w, w)
        y2: int = self._wobble(h, h)

        x3: int = self._wobble(0, w)
        y3: int = self._wobble(h, h)

        # put image fully in frame
        adj_x = abs(min(x0, x1, x2, x3))
        adj_y = abs(min(y0, y1, y2, y3))
        return ([(x0 + adj_x, y0 + adj_y),
                 (x1 + adj_x, y1 + adj_y),
                 (x2 + adj_x, y2 + adj_y),
                 (x3 + adj_x, y3 + adj_y)],
                [(0, 0), (w, 0), (w, h), (0, h)])

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata = super().update_metadata(metadata)
        metadata[0]["parameters"]["wobble_percent"] = self.wobble_percent
        metadata[0]["parameters"]["pa"] = self.pa
        metadata[0]["parameters"]["pb"] = self.pb
        return metadata


class RotateTransformation(ImageTransformationInterface):
    def __init__(self, angle: int):
        self.angle = angle

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        return image.rotate(self.angle, expand=True)

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "rotate",
             "method": "PIL.Image.Image.rotate",
             "parameters": {"angle": self.angle}})
        return metadata


class RandomRotateTransformation(RotateTransformation):
    def __init__(self):
        super().__init__(random.randint(0, 359))


class AutocontrastTransformation(ImageTransformationInterface):
    def __init__(self, cutoff: int):
        self.cutoff = cutoff

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        return ImageOps.autocontrast(image, self.cutoff)

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "autocontrast",
             "method": "PIL.ImageOps.autocontrast",
             "parameters": {"cutoff": self.cutoff}})
        return metadata


class RandomAutocontrastTransformation(AutocontrastTransformation):
    def __init__(self):
        super().__init__(random.randint(0, 40))


class PosterizeTransformation(ImageTransformationInterface):
    def __init__(self, bits: int):
        self.bits = bits

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        return ImageOps.posterize(image, self.bits)

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "posterize",
             "method": "PIL.ImageOps.posterize",
             "parameters": {"bits": self.bits}})
        return metadata


class RandomPosterizeTransformation(PosterizeTransformation):
    def __init__(self):
        super().__init__(random.randint(1, 8))


class SolarizeTransformation(ImageTransformationInterface):
    def __init__(self, threshold: int):
        self.threshold = threshold

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        return ImageOps.solarize(image, self.threshold)

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "solarize",
             "method": "PIL.ImageOps.solarize",
             "parameters": {"threshold": self.threshold}})
        return metadata


class RandomSolarizeTransformation(SolarizeTransformation):
    def __init__(self):
        super().__init__(random.randint(1, 128))


class RandomChoiceTransformation(ImageTransformationInterface):
    def __init__(self, transformations: list[ImageTransformationInterface]):
        self.transformations = transformations
        self._chosen = None

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        self._chosen = random.choice(self.transformations)
        return self._chosen.apply_transformation(image)

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        if self._chosen:
            return self._chosen.update_metadata(metadata)
        else:
            raise ValueError("No transformation chosen")


class SolidColorBackgroundPasteTransformation(ImageTransformationInterface):
    def __init__(self, color: Tuple[int, int, int], position: Tuple[int, int], size: Tuple[int, int],
                 mask: Image.Image = None):
        self.color = color
        self.position = position
        self.size = size
        self.mask = mask

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        bg = Image.new("RGBA", self.size, self.color)
        mask = self.mask if self.mask else image
        bg.paste(image, self.position, mask)
        return bg

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "paste",
             "method": "PIL.Image.Image.paste",
             "parameters": {"color": self.color, "position": self.position, "size": self.size, "mask": self.mask}})
        return metadata


class RandomSolidColorBackgroundPasteTransformation(SolidColorBackgroundPasteTransformation):
    def __init__(self, position: Tuple[int, int], size: Tuple[int, int], mask: Image.Image = None):
        super().__init__(
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            position,
            size,
            mask
        )


def _random_position(bg_size: Tuple[int, int],
                     img_size: Tuple[int, int],
                     limit: float) -> (Tuple[int, int], dict):
    x_start = 0 - int(img_size[0] * (1 - limit))
    x_end = int(bg_size[0] - img_size[0] + (img_size[0] * (1 - limit)))
    y_start = 0 - int(img_size[1] * (1 - limit))
    y_end = int(bg_size[1] - img_size[1] + (img_size[1] * (1 - limit)))
    return random.randint(x_start, x_end), random.randint(y_start, y_end)


class LegacyRandomSolidColorBackgroundPasteTransformation(ImageTransformationInterface):
    def __init__(self, size: Tuple[int, int], position_limit: float = 0.75):
        self.size = size
        self.position_limit = position_limit
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.position = None

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        bg = Image.new("RGBA", self.size, self.color)
        self.position = _random_position(self.size, image.size, self.position_limit)
        bg.paste(image, self.position, image.split()[3])
        return bg

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "paste",
             "method": "PIL.Image.Image.paste",
             "parameters": {"color": self.color, "position_limit": self.position_limit, "position": self.position}})
        return metadata


class LegacyRandomImageBackgroundPasteTransformation(ImageTransformationInterface):
    def __init__(self, size: Tuple[int, int], position_limit: float = 0.75):
        self.size = size
        self.position_limit = position_limit
        self.bg_image = Image.open(
            random.choice([i for i in pathlib.Path().glob("data/backgrounds/*")]))
        self.position = None

    def apply_transformation(self, image: Image.Image) -> Image.Image:
        bg = Image.new("RGBA", self.size)
        bg.paste(self.bg_image.resize(self.size), (0, 0))
        self.position = _random_position(self.size, image.size, self.position_limit)
        bg.paste(image, self.position, image.split()[3])
        return bg

    def update_metadata(self, metadata: list[dict]) -> list[dict]:
        metadata.append(
            {"class": self.__class__,
             "type": "paste",
             "method": "PIL.Image.Image.paste",
             "parameters": {"bg_image": self.bg_image.filename, "position_limit": self.position_limit,
                            "position": self.position}})
        return metadata
