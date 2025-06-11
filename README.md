# Collectable Card Identifier

## Description

The Collectable Card Identifier project focuses on generating and managing datasets to train image classifiers for identifying individual cards from various Trading Card Games (TCG) and Collectible Card Games (CCG). Starting with "Pokemon" and expanding to "Magic: The Gathering" and "YuGiOh!", this system can be used for applications like inventory management, automated sorting, and card valuation.

The primary goal is to create a dataset generator that produces a diverse and extensive training dataset through various image transformations. This dataset will support the broader objective of developing a card sorting robot and other related applications.

## Installation

This project uses [Poetry](https://python-poetry.org/) to manage dependencies and requires **Python 3.10**. After cloning the repository, install the project and its dependencies by running:

```bash
poetry install
```

After installing dependencies, enable git hooks so style checks and tests run
automatically before each commit:

```bash
pre-commit install
```

This will create an isolated virtual environment and install all runtime and
development dependencies. If you prefer not to use Poetry, install the package
with `pip` and include the `[dev]` extras:

```bash
pip install ".[dev]"
```

Using `[dev]` installs `pytest`, `ruff`, `pre-commit`, and other development
tools. Either method will make the `mkdataset` command available in your
environment.

## Environment Variables

Several environment variables control where datasets and images are stored. They all default to sub-directories of `data` if not set.

| Variable | Description | Default |
|----------|-------------|---------|
| `CARDIDENT_DATA_ROOT` | Root directory for all data assets. | `data` |
| `CARDIDENT_BACKGROUNDS_DIR` | Location of background images. | `$CARDIDENT_DATA_ROOT/backgrounds` |
| `CARDIDENT_IMAGES_DIR` | Where original card images are downloaded. | `$CARDIDENT_DATA_ROOT/images/originals` |
| `CARDIDENT_DATASETS_DIR` | Destination for generated dataset images. | `$CARDIDENT_DATA_ROOT/images/dataset` |
| `CARDIDENT_DEBUG` | Enable debug logging across multiprocessing workers. | `0` |

## Usage

First ensure card images are downloaded. For Pokémon cards this can be done with:

```bash
poetry run mkdataset card-data -t pokemon --images
```

Generate a dataset of 500 images:

```bash
poetry run mkdataset create-dataset -t pokemon -n 500
```

## Dataset Organization and Workflow

All data lives beneath `CARDIDENT_DATA_ROOT` (defaults to `data`).
Important subdirectories are:

```
$CARDIDENT_DATA_ROOT/
  backgrounds/           # background images used for dataset generation
  barrel/<game>/         # pickled state files and RNG snapshots
  images/
    originals/<game>/    # downloaded card scans
    dataset/<game>/      # generated dataset images
```

Generated datasets are stored by set and card ID. For example:

```
$CARDIDENT_DATA_ROOT/images/dataset/pokemon/<set>/<card-id>/*.png
```

Training symlinks produced by `DatasetManager.mk_symlinks` are placed in
`dataset/<game>/symlinks/<mode>` where `<mode>` is `all`, `legal`, or `sets`.

A typical workflow is:

1. Download card metadata and images:

   ```bash
   poetry run mkdataset card-data -t pokemon --refresh --images
   ```

2. Generate randomized dataset images (populate
   `CARDIDENT_BACKGROUNDS_DIR` with background images first):

   ```bash
   poetry run mkdataset create-dataset -t pokemon -n 500
   ```

3. Trim each card directory to the desired size:

   ```bash
   poetry run mkdataset trim-dataset -t pokemon -n 200
   ```

4. Create symlink trees for training:

   ```python
   from card_identifier.dataset import DatasetManager
   dm = DatasetManager("pokemon")
   dm.mk_symlinks("all")  # or 'legal'/'sets'
   ```

## Debug Logging

Set `CARDIDENT_DEBUG=1` to enable debug messages from all worker processes. The
`--debug` flag in the CLI sets this variable automatically.

## Running Tests

Execute the test suite before committing changes:

```bash
poetry run pytest -n auto
```

The test suite depends on additional packages like `pytest-xdist`, `Pillow`, and
`pokemontcgsdk`. These are included when installing with the `[dev]` extras.

You can also run all style checks and tests at once with:

```bash
pre-commit run --all-files
```

## Linting

Run Ruff to check code style and common errors:

```bash
poetry run ruff check .
```
