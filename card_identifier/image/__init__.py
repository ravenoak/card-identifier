import hashlib
import pathlib
import random

from PIL import Image

from . import background
from . import transformers

# WORKING_SIZE = (500, 500)
WORKING_SIZE = (1024, 1024)
# OUT_SIZE = (224, 224)
OUT_SIZE = WORKING_SIZE
OUT_EXT = "png"


def gen_random_dataset(image_id: str,
                       image_path: pathlib.Path,
                       dataset_path: pathlib.Path,
                       dataset_size: int):
    if not image_path.exists() and image_path.is_file():
        # TODO: Actually might be an error...
        return
    save_path = dataset_path.joinpath(image_id)
    if not save_path.exists():
        save_path.mkdir(parents=True)

    src_image = Image.open(image_path)
    src_image.putalpha(255)
    for _ in range(0, dataset_size):
        meta = {}
        bg_color = background.random_solid_color()
        meta['bg_color'] = bg_color
        base_image = Image.new("RGBA", WORKING_SIZE, bg_color)
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
            filename = f"{image_hash}.{OUT_EXT}"
            xform_image.resize(OUT_SIZE).save(
                open(save_path.joinpath(filename), "wb"), OUT_EXT)
        else:
            image_hash = hashlib.sha256(base_image.tobytes()).hexdigest()
            filename = f"{image_hash}.{OUT_EXT}"
            base_image.resize(OUT_SIZE).save(
                open(save_path.joinpath(filename), "wb"), OUT_EXT)
