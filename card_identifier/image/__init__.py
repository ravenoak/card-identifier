import pathlib
import random

from PIL import Image

from . import background
from . import transformers

WORKING_SIZE = (500, 500)
OUT_SIZE = (224, 224)
OUT_EXT = "png"


def gen_dataset(image_id: str,
                image_path: pathlib.Path,
                dataset_path: pathlib.Path,
                save_percent=0.01):
    if not image_path.exists() and image_path.is_file():
        # TODO: Actually might be an error...
        return
    save_path = dataset_path.joinpath(image_id)
    if not save_path.exists():
        save_path.mkdir(parents=True)

    img = Image.open(image_path)
    for bg_color in background.range_solid_colors():
        bg_img, bg_label = background.mk_background(WORKING_SIZE, bg_color)
        #resize_label = "resize-0"
        #if random.random() < 0.5:
        resized_img, resize_label = transformers.random_resize(img)
        for rot_img, rot_label in transformers.range_rotate(resized_img, bg_color):
            for pos, pos_label in background.range_placement(bg_img.size,
                                                             rot_img.size,
                                                             0.75):
                pos_img = bg_img.copy()
                pos_img.paste(rot_img, pos)
                if random.random() < save_percent:
                    filename = f"{image_id}.{resize_label}.{bg_label}." \
                               f"{rot_label}.{pos_label}.{OUT_EXT}"
                    print(f"saving image: {filename}")
                    pos_img.resize(OUT_SIZE).save(
                        open(save_path.joinpath(filename), "wb"), OUT_EXT)
                for xform_img, xform_label in transformers.range_transformers(
                        pos_img, "all"):
                    if random.random() < save_percent:
                        filename = f"{image_id}.{resize_label}.{bg_label}." \
                                   f"{rot_label}.{pos_label}.{xform_label}." \
                                   f"{OUT_EXT}"
                        print(f"saving image: {filename}")
                        xform_img.resize(OUT_SIZE).save(
                            open(save_path.joinpath(filename), "wb"), OUT_EXT)
