# Collectable Card Identifier

## Description

The Collectable Card Identifier project identifies individual trading cards from photographs. It starts with the Pokémon TCG and is built to take Magic: The Gathering and Yu-Gi-Oh! later. It has two parts:

1. **Dataset manager.** It fetches card data and one scan per card, then generates many randomized training images per card, and selects any subset of cards for a dataset (a set, a series, only the cards legal in Standard).
2. **Identifier.** It trains models on a selected dataset, evaluates them on real photos, and identifies cards and their labels. More than one architecture is trainable.

The first consumer is a card sorting robot. Inventory and valuation tools follow.

The dataset manager exists today and has known defects. The identifier is planned. Start with [docs/intent.md](docs/intent.md) for the purpose, [docs/specs/](docs/specs/) for the requirements, and the [GitHub issues](https://github.com/ravenoak/card-identifier/issues) for the backlog. [docs/README.md](docs/README.md) explains how intent, specs, decisions and issues fit together.

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

## Licensing and data

The code is AGPL-3.0-or-later. Card images belong to their owners. This project downloads them for local training, keeps them out of git and out of container images, and does not redistribute them. Pretrained model weights carry their own licences, and some forbid commercial use. See [docs/intent.md](docs/intent.md) for the constraints.
