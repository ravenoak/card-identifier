import pathlib

from .config import config

PICKLE_LOCATION = "barrel"
NAMESPACES = ["pokemon"]


def get_pickle_dir(namespace: str) -> pathlib.Path:
    if namespace not in NAMESPACES:
        raise ValueError(f"namespace {namespace} not in {NAMESPACES}")
    path = config.data_root.joinpath(PICKLE_LOCATION, namespace)
    if not path.exists():
        path.mkdir(parents=True)
    return path


def get_image_dir(namespace: str) -> pathlib.Path:
    if namespace not in NAMESPACES:
        raise ValueError(f"namespace {namespace} not in {NAMESPACES}")
    path = config.images_dir.joinpath(namespace)
    if not path.exists():
        path.mkdir(parents=True)
    return path


def get_dataset_dir(namespace: str) -> pathlib.Path:
    if namespace not in NAMESPACES:
        raise ValueError(f"namespace {namespace} not in {NAMESPACES}")
    path = config.datasets_dir.joinpath(namespace)
    if not path.exists():
        path.mkdir(parents=True)
    return path
