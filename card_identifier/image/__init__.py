import logging

from PIL import Image

from . import background
from . import transformers

func_map = {
    "random_solid_color": background.random_solid_color,
    "random_bg_image": background.random_bg_image,
}

logger = logging.getLogger("card_identifier.image")


class Pipeline:
    def __init__(self, transformations: list[transformers.ImageTransformationInterface] = None):
        self.transformations = transformations or []

    def add_transformation(self, transformation: transformers.ImageTransformationInterface):
        self.transformations.append(transformation)

    def execute(self, image: Image.Image) -> tuple[Image.Image, dict]:
        metadata = []
        for transformation in self.transformations:
            image = transformation.apply_transformation(image)
            metadata = transformation.update_metadata(metadata)
        return image, metadata
