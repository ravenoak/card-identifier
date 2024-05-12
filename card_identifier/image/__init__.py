import logging

from PIL import Image

from . import transformers

logger = logging.getLogger("card_identifier.image")


class Pipeline:
    """Pipeline for applying transformations to an image"""

    def __init__(self, transformations: list[transformers.ImageTransformationInterface] = None):
        self._transformations = transformations or []

    def add_transformation(self, transformation: transformers.ImageTransformationInterface):
        """Adds a transformation to the pipeline"""
        self._transformations.append(transformation)

    def execute(self, image: Image.Image) -> tuple[Image.Image, dict]:
        """Executes the pipeline on the image"""
        metadata = []
        for transformation in self._transformations:
            image = transformation.apply_transformation(image)
            metadata = transformation.update_metadata(metadata)
        return image, metadata
