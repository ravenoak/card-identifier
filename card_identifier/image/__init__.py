import hashlib
import pathlib
import pickle
import random
from typing import Dict, Union

from PIL import Image

from card_identifier.data import get_image_dir, get_dataset_dir
from . import background
from . import transformers

DEFAULT_WORKING_SIZE = (1024, 1024)
DEFAULT_OUT_SIZE = (224, 224)
DEFAULT_OUT_EXT = "png"

func_map = {
    "random_solid_color": background.random_solid_color,
    "random_bg_image": background.random_bg_image,
}


class ImageDatasetManager:
    def __init__(self, namespace: str):
        self.working_size = DEFAULT_WORKING_SIZE
        self.out_size = DEFAULT_OUT_SIZE
        self.out_ext = DEFAULT_OUT_EXT
        self.namespace = namespace
        self.image_dir = get_image_dir(namespace)
        self.dataset_dir = get_dataset_dir(namespace)
        self.card_dataset_map = self.load_card_dataset_map()
        self.num_img_desired = 100

    def load_card_dataset_map(self) -> Dict[str, pathlib.Path]:
        if self.dataset_dir.joinpath("card_dataset_map.pickle").exists():
            with open(self.dataset_dir.joinpath(
                    "card_dataset_map.pickle"), "rb") as file:
                return pickle.load(file)
        else:
            return {}

    def save_card_dataset_map(self):
        with open(self.dataset_dir.joinpath(
                "card_dataset_map.pickle"), "wb") as file:
            pickle.dump(self.card_dataset_map, file)

    def scan_dataset_dir(self) -> dict[str, dict[str, Union[int, list]]]:
        card_dataset_map = {}
        for img in self.dataset_dir.glob('**/*.png'):
            _id = img.parts[5]
            if not card_dataset_map.get(_id):
                card_dataset_map[_id] = {'num_img': 0, 'img_paths': []}
            card_dataset_map[_id]['img_paths'].append(pathlib.Path(img))
            card_dataset_map[_id]['num_img'] += 1
        return card_dataset_map


def gen_random_dataset(image_path: pathlib.Path,
                       save_path: pathlib.Path,
                       dataset_size: int):
    if not image_path.exists() and image_path.is_file():
        # TODO: Actually might be an error...
        return
    if not save_path.exists():
        raise ValueError(f"Save path does not exist: {save_path}")

    src_image = Image.open(image_path)
    src_image.putalpha(255)
    for _ in range(0, dataset_size):
        meta = {}
        bg_type = random.choice(background.BACKGROUND_TYPES)
        # TODO: Figure out what to to with the meta data.
        meta['bg_type'] = bg_type
        base_image = func_map[bg_type](DEFAULT_WORKING_SIZE, meta)
        # TODO: Add logging.
        # print(bg_type, base_image, meta)
        resized_img, resize_meta = transformers.random_resize(src_image)
        meta.update(resize_meta)
        rot_image, rot_meta = transformers.random_rotate(resized_img)
        meta.update(rot_meta)
        pos, pos_meta = background.random_placement(base_image.size,
                                                    rot_image.size,
                                                    0.75)
        meta.update(pos_meta)
        base_image.paste(rot_image, pos, rot_image)
        base_image = base_image.convert(mode="RGB")
        # xform = random.choice([True, False])
        xform = False
        if xform:
            meta['transform'] = True
            xform_image, xform_meta = transformers.random_random_transformer(
                base_image)
            meta.update(xform_meta)
            image_hash = hashlib.sha256(xform_image.tobytes()).hexdigest()
            filename = f"{image_hash}.{DEFAULT_OUT_EXT}"
            xform_image.resize(DEFAULT_OUT_SIZE).save(
                open(save_path.joinpath(filename), "wb"), DEFAULT_OUT_EXT)
        else:
            image_hash = hashlib.sha256(base_image.tobytes()).hexdigest()
            filename = f"{image_hash}.{DEFAULT_OUT_EXT}"
            base_image.resize(DEFAULT_OUT_SIZE).save(
                open(save_path.joinpath(filename), "wb"), DEFAULT_OUT_EXT)
