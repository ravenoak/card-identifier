import logging
import pathlib
import pickle
import random
from typing import Any

logger = logging.getLogger(__name__)


def save_pickle(obj: Any, path: pathlib.Path) -> None:
    """Serialize *obj* to *path* using pickle."""
    with open(path, "wb") as file:
        pickle.dump(obj, file)


def load_pickle(path: pathlib.Path, default: Any | None = None) -> Any | None:
    """Load a pickle from *path*, returning *default* if the file is missing."""
    if path.exists():
        with open(path, "rb") as file:
            logger.info(f"opening pickle {path}")
            return pickle.load(file)
    logger.info(f"not loading pickle: missing {path}")
    return default


def save_random_state(pickle_dir: pathlib.Path) -> None:
    """Save Python's global random state to *pickle_dir*."""
    save_pickle(random.getstate(), pickle_dir.joinpath("random_state.pickle"))


def load_random_state(pickle_dir: pathlib.Path) -> None:
    """Load Python's global random state from *pickle_dir* if present."""
    state = load_pickle(pickle_dir.joinpath("random_state.pickle"))
    if state is not None:
        random.setstate(state)
