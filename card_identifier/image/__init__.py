import logging

from PIL import Image

from . import transformers
from card_identifier.metadata import ImageMetadata

logger = logging.getLogger("card_identifier.image")


class Pipeline:
    """Pipeline for applying transformations to an image"""

    def __init__(self, transformations: list[transformers.ImageTransformationInterface] = None):
        self._transformations = transformations or []

    def add_transformation(self, transformation: transformers.ImageTransformationInterface):
        """Adds a transformation to the pipeline"""
        self._transformations.append(transformation)

    def execute(self, image: Image.Image, metadata: ImageMetadata) -> tuple[Image.Image, ImageMetadata]:
        """Executes the pipeline on the image"""
        for transformation in self._transformations:
            image = transformation.apply_transformation(image)
            metadata.transformation_metadata.append(transformation.get_metadata())
        return image, metadata
