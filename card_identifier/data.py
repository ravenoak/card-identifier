import pathlib

DATA_LOCATION = "data"
PICKLE_LOCATION = "barrel"
IMAGE_LOCATION = "images"


def get_pickle_dir() -> pathlib.Path:
    path = pathlib.Path(DATA_LOCATION).joinpath(pathlib.Path(PICKLE_LOCATION))
    if not path.exists():
        path.mkdir(parents=True)
    return path


def get_image_dir() -> pathlib.Path:
    path = pathlib.Path(DATA_LOCATION). \
        joinpath(pathlib.Path(IMAGE_LOCATION)). \
        joinpath("originals")
    if not path.exists():
        path.mkdir(parents=True)
    return path


def get_dataset_dir() -> pathlib.Path:
    path = pathlib.Path(DATA_LOCATION). \
        joinpath(pathlib.Path(IMAGE_LOCATION)). \
        joinpath("dataset")
    if not path.exists():
        path.mkdir(parents=True)
    return path
