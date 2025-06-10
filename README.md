# Collectable Card Identifier

## Description

The Collectable Card Identifier project focuses on generating and managing datasets to train image classifiers for identifying individual cards from various Trading Card Games (TCG) and Collectible Card Games (CCG). Starting with "Pokemon" and expanding to "Magic: The Gathering" and "YuGiOh!", this system can be used for applications like inventory management, automated sorting, and card valuation.

The primary goal is to create a dataset generator that produces a diverse and extensive training dataset through various image transformations. This dataset will support the broader objective of developing a card sorting robot and other related applications.

## Installation

This project uses [Poetry](https://python-poetry.org/) to manage dependencies and requires **Python 3.10**. After cloning the repository, install the project and its dependencies by running:

```bash
poetry install
```

This will create an isolated virtual environment and install all runtime and development dependencies. You can also install the package with `pip` for development:

```bash
pip install -e .
```

Either method will make the `mkdataset` command available in your environment.

## Environment Variables

Several environment variables control where datasets and images are stored. They all default to sub-directories of `data` if not set.

| Variable | Description | Default |
|----------|-------------|---------|
| `CARDIDENT_DATA_ROOT` | Root directory for all data assets. | `data` |
| `CARDIDENT_BACKGROUNDS_DIR` | Location of background images. | `$CARDIDENT_DATA_ROOT/backgrounds` |
| `CARDIDENT_IMAGES_DIR` | Where original card images are downloaded. | `$CARDIDENT_DATA_ROOT/images/originals` |
| `CARDIDENT_DATASETS_DIR` | Destination for generated dataset images. | `$CARDIDENT_DATA_ROOT/images/dataset` |

## Usage

First ensure card images are downloaded. For Pokémon cards this can be done with:

```bash
poetry run mkdataset card-data -t pokemon --images
```

Generate a dataset of 500 images:

```bash
poetry run mkdataset create-dataset -t pokemon -n 500
```

## Running Tests

Execute the test suite before committing changes:

```bash
poetry run pytest -n auto
```
