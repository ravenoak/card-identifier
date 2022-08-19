import pathlib

DATA_LOCATION = "data"
PICKLE_LOCATION = "barrel"
IMAGE_LOCATION = "images"
NAMESPACES = ["pokemon"]


def get_pickle_dir(namespace: str) -> pathlib.Path:
    if namespace not in NAMESPACES:
        raise ValueError(f"namespace {namespace} not in {NAMESPACES}")
    path = pathlib.Path(DATA_LOCATION). \
        joinpath(pathlib.Path(PICKLE_LOCATION)). \
        joinpath(pathlib.Path(namespace))
    if not path.exists():
        path.mkdir(parents=True)
    return path


def get_image_dir(namespace: str) -> pathlib.Path:
    if namespace not in NAMESPACES:
        raise ValueError(f"namespace {namespace} not in {NAMESPACES}")
    path = pathlib.Path(DATA_LOCATION). \
        joinpath(pathlib.Path(IMAGE_LOCATION)). \
        joinpath(pathlib.Path("originals")). \
        joinpath(pathlib.Path(namespace))
    if not path.exists():
        path.mkdir(parents=True)
    return path


def get_dataset_dir(namespace: str) -> pathlib.Path:
    if namespace not in NAMESPACES:
        raise ValueError(f"namespace {namespace} not in {NAMESPACES}")
    path = pathlib.Path(DATA_LOCATION). \
        joinpath(pathlib.Path(IMAGE_LOCATION)). \
        joinpath(pathlib.Path("dataset")). \
        joinpath(pathlib.Path(namespace))
    if not path.exists():
        path.mkdir(parents=True)
    return path
