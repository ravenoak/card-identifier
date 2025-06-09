import logging

from . import background
from . import transformers  # noqa: F401

func_map = {
    "random_solid_color": background.random_solid_color,
    "random_bg_image": background.random_bg_image,
}

logger = logging.getLogger("card_identifier.image")
