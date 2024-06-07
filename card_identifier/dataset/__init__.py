import hashlib
import logging
import random

from PIL import Image

from card_identifier.image import transformers, Pipeline
from card_identifier.metadata import metadata_writer, ImageMetadata
from card_identifier.util import setup_logging

DEFAULT_WORKING_SIZE = (1024, 1024)
DEFAULT_OUT_SIZE = (224, 224)
DEFAULT_OUT_EXT = "png"

logger = logging.getLogger("card_identifier.dataset")


def gen_random_dataset(card_id: str, dataset_size: int, subject_noise=False):
    """Generates a random dataset of the given size from the given image."""
    # TODO: Need to handle logging better in multiprocessing.
    setup_logging(debug=False)
    logger.info(f"Generating {dataset_size} images from {card_id}")
    src_image = Image.open(card_id)
    src_image = src_image.convert(mode="RGBA")
    for iteration in range(0, dataset_size):
        logger.debug(f"Generating image {card_id} {iteration} of {dataset_size}")
        pipeline = Pipeline()
        if subject_noise and random.random() < 0.5:
            pipeline.add_transformation(transformers.RandomChoiceTransformation([
                transformers.RandomSolarizeTransformation(),
                transformers.RandomPosterizeTransformation(),
                transformers.RandomAutocontrastTransformation(),
            ]))
        pipeline.add_transformation(transformers.RandomPercentResizeTransformation(0.3, 1.6))
        pipeline.add_transformation(transformers.WobblePerspectiveTransformation(src_image.size, 0.3))
        pipeline.add_transformation(transformers.RandomRotateTransformation())
        pipeline.add_transformation(transformers.RandomChoiceTransformation([
            transformers.LegacyRandomSolidColorBackgroundPasteTransformation(DEFAULT_WORKING_SIZE),
            transformers.LegacyRandomImageBackgroundPasteTransformation(DEFAULT_WORKING_SIZE),
        ]))
        meta = ImageMetadata(card_id="", transformation_metadata=[], image_hash="")
        image, meta = pipeline.execute(src_image, meta)
        image = image.convert(mode="RGB")
        image_hash = hashlib.sha256(image.tobytes()).hexdigest()
        meta.image_hash = image_hash
        filename = f"{image_hash}.{DEFAULT_OUT_EXT}"
        meta.image_path = filename
        image = image.resize(DEFAULT_OUT_SIZE)
        metadata_writer.write({"filename": filename, **meta})
        logger.debug(f"Generated image with meta: {meta}")
