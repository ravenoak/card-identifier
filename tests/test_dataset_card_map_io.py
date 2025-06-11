import pickle
from pathlib import Path

from card_identifier.dataset import DatasetManager


def _setup_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = Path(tmp_path)
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"

    return config.datasets_dir / "pokemon"


def test_save_card_dataset_map_writes_pickle(tmp_path, monkeypatch):
    dataset_dir = _setup_paths(tmp_path, monkeypatch)
    dm = DatasetManager("pokemon")
    dm.card_dataset_map = {"c1": {"num_img": 1}}

    dm.save_card_dataset_map()

    pickle_path = dataset_dir / DatasetManager.CARD_IMAGE_MAP
    assert pickle_path.exists()
    with open(pickle_path, "rb") as fh:
        assert pickle.load(fh) == dm.card_dataset_map


def test_load_card_dataset_map_reads_pickle(tmp_path, monkeypatch):
    dataset_dir = _setup_paths(tmp_path, monkeypatch)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    expected = {"c2": {"num_img": 2}}
    with open(dataset_dir / DatasetManager.CARD_IMAGE_MAP, "wb") as fh:
        pickle.dump(expected, fh)

    dm = DatasetManager("pokemon")
    result = dm.load_card_dataset_map()

    assert result == expected
