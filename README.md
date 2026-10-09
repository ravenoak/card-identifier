# Collectable Card Identifier

## Description

The Collectable Card Identifier project focuses on generating and managing datasets to train image classifiers for identifying individual cards from various Trading Card Games (TCG) and Collectible Card Games (CCG). Starting with "Pokemon" and expanding to "Magic: The Gathering" and "YuGiOh!", this system can be used for applications like inventory management, automated sorting, and card valuation.

The primary goal is to create a dataset generator that produces a diverse and extensive training dataset through various image transformations. This dataset will support the broader objective of developing a card sorting robot and other related applications.

## Installation

This project uses [uv](https://docs.astral.sh/uv/) to manage dependencies and
requires **Python 3.13 or newer**. After cloning the repository, install the
project and its development tools:

```bash
uv sync
```

This creates `.venv`, installs the locked runtime and `dev` dependencies, and
makes the `mkdataset` command available through `uv run`.

Enable the git hook with [prek](https://prek.j178.dev/) so ruff, pyright and
pytest run before each commit:

```bash
uv run prek install
```

The optional Streamlit demo in `scripts/streamlit` needs its own dependency
group: `uv sync --group streamlit`.

Helper tasks (container builds, model training) run with
[go-task](https://taskfile.dev). `task --list` shows them.

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
uv run mkdataset card-data -t pokemon --images
```

Generate a dataset of 500 images:

```bash
uv run mkdataset create-dataset -t pokemon -n 500
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
   uv run mkdataset card-data -t pokemon --refresh --images
   ```

2. Generate randomized dataset images (populate
   `CARDIDENT_BACKGROUNDS_DIR` with background images first):

   ```bash
   uv run mkdataset create-dataset -t pokemon -n 500
   ```

3. Trim each card directory to the desired size:

   ```bash
   uv run mkdataset trim-dataset -t pokemon -n 200
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

`uv sync` installs the test dependencies. Run the test suite before committing
changes:

```bash
uv run pytest -n auto
```

Run every check (formatting, lint, type check and tests) at once with:

```bash
uv run prek run --all-files
```

## Linting and Type Checking

Each check also runs on its own:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

[pyright](https://github.com/microsoft/pyright) reads its settings from
`[tool.pyright]` in `pyproject.toml` and finds packages in `.venv`, so editors
and language servers that run `pyright-langserver` from the repository root
need no extra setup after `uv sync`.
