# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Python 3.13+, managed with uv. Setup: `uv sync`, then `uv run prek install` for the git hook.

- All checks (ruff check, ruff format, pyright, pytest): `uv run prek run --all-files`
- Tests: `uv run pytest -n auto`. One test: `uv run pytest tests/test_dataset_builder.py::test_name`
- Lint, format, types: `uv run ruff check .`, `uv run ruff format .`, `uv run pyright`
- CLI: `uv run mkdataset <command>` (`card-data`, `create-dataset`, `trim-dataset`, `save-random-state`). Pass `--debug` before the command.
- Container and training tasks: `task --list` (go-task, see `Taskfile.yml`)

`AGENTS.md` requires `ruff format` and a passing `uv run pytest -n auto` before every commit. The pytest config is `strict = true`. Pyright runs in `standard` mode and skips `scripts/label_image.py` and `scripts/streamlit`. Ruff skips `notebooks/`. CI runs the prek hooks on Python 3.13 and 3.14.

## Architecture

The project generates training images for card classifiers. It takes one downloaded scan per card and produces many randomized variants. Only the `pokemon` game exists today. `data.NAMESPACES` is the list of games, and every path helper raises `ValueError` for a name outside it.

Pipeline, one stage per CLI command:

1. `card-data` (`cli/card_data.py`): `cards.pokemon.CardManager` fetches card and set metadata through `pokemontcgsdk` and caches it as pickles. `ImageManager` downloads each card's large image to `<images_dir>/pokemon/<card-id>.png` and writes `card_image_map.pickle` (card id to filename).
2. `create-dataset` (`cli/create_dataset.py`): `dataset.generator.DatasetBuilder` reads `card_image_map.pickle`, skips cards that already have enough images, and runs `gen_random_dataset` per card in a `spawn` multiprocessing pool. Each output is a 224x224 PNG named by the SHA-256 of its pixels, with a `.json` sidecar describing the transforms. Files go to `<datasets_dir>/pokemon/<set-id>/<card-id>/`.
3. `trim-dataset`: cuts each card directory down to N images.
4. `dataset.DatasetManager.mk_symlinks(mode)` (library call, no CLI): builds `symlinks/{all,legal,sets}` trees for training. `legal` calls the live Pokemon API through `get_legal_sets`.

Each image's transform chain lives in `gen_random_dataset`: optional noise or other transformer, random resize, perspective, rotate, then paste onto a random background (solid color or an image from the backgrounds dir). The transformers in `image/transformers.py` and backgrounds in `image/background.py` each return `(image, meta_dict)`. The meta dicts accumulate into the sidecar JSON.

Things that need more than one file to see:

- **Paths.** `config.PathsConfig` reads the `CARDIDENT_*` environment variables once, at import. `data.get_*_dir` creates the directory on first call. State pickles live under `<data_root>/barrel/<game>/`.
- **Two `card_image_map.pickle` files.** `DatasetBuilder` reads the card-id-to-original-image map from `barrel/<game>/`. `DatasetManager` keeps a different map (card id to generated images) in the dataset directory under the same filename.
- **Reproducibility.** `storage.save_random_state` and `load_random_state` pickle Python's `random` state in `barrel/`. `DatasetBuilder.build_work` loads it before drawing work.
- **Debug logging in workers.** Spawned workers do not inherit logging config. `DatasetBuilder.run` copies the debug flag into `CARDIDENT_DEBUG`, and `gen_random_dataset` calls `setup_logging` from it.
- **Pokemon API workarounds.** The SDK's `Set` class fails on new sets that lack `printedTotal`. `cards/pokemon/api_client.py` defines `PokemonSet` with it optional, and `get_legal_sets` uses a minimal `_SetId`. Tests use the `new_set` fixture in `tests/conftest.py`.
- **Game support.** A new game subclasses `cards.base.BaseCardManager` and must be added to `data.NAMESPACES`. `cli/card_data.py` dispatches on `card_type` by hand.

Outside the package: `deploy/` has the Dockerfiles. `scripts/run_mkimgclsfr.sh` trains with TensorFlow Hub's `make_image_classifier` (see `docs/model_training.md`). `notebooks/` and `scripts/streamlit` are experiments, and the Streamlit demo needs `uv sync --group streamlit`. `DESIGN.md` holds the product goals.
