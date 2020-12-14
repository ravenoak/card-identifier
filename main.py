import argparse
import pathlib
import pickle

#from .image import gen_dataset

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


# def create_training_images(save_percent: float = 0.01):
#     pickle_dir = get_pickle_dir()
#     with open(pickle_dir.joinpath("id_image_map.pickle"), "rb") as file:
#         id_image_map = pickle.load(file)
#     for id, path in id_image_map:
#         print(id, path)
#         gen_dataset(id, path, get_dataset_dir(), save_percent)


def main(args):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scripts for working with card-identifier')
    subparsers = parser.add_subparsers()
    pokemon = subparsers.add_parser('pokemon')
