from pathlib import Path

import pytest


def _create_dataset(tmp_path: Path) -> Path:
    root = tmp_path / "images" / "dataset" / "pokemon"
    (root / "s1" / "s1-c1").mkdir(parents=True)
    (root / "s2" / "s2-c2").mkdir(parents=True)
    (root / "s1" / "s1-c1" / "img1.png").write_bytes(b"1")
    (root / "s2" / "s2-c2" / "img2.png").write_bytes(b"2")
    return root


def test_mk_symlinks_all(tmp_path, monkeypatch):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = Path(tmp_path)
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"
    dataset_root = _create_dataset(tmp_path)
    from card_identifier.dataset import DatasetManager

    dm = DatasetManager("pokemon")
    dm.mk_symlinks("all")
    link = dataset_root / "symlinks" / "all" / "s1-c1" / "img1.png"
    assert link.is_symlink()
    assert link.resolve() == dataset_root / "s1" / "s1-c1" / "img1.png"
    link2 = dataset_root / "symlinks" / "all" / "s2-c2" / "img2.png"
    assert link2.is_symlink()


def test_mk_symlinks_legal(tmp_path, monkeypatch):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = Path(tmp_path)
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"
    dataset_root = _create_dataset(tmp_path)
    monkeypatch.setattr("card_identifier.dataset.get_legal_sets", lambda: {"s1"})
    from card_identifier.dataset import DatasetManager

    dm = DatasetManager("pokemon")
    dm.mk_symlinks("legal")
    link = dataset_root / "symlinks" / "legal" / "s1-c1" / "img1.png"
    assert link.is_symlink()
    link2 = dataset_root / "symlinks" / "legal" / "s2-c2" / "img2.png"
    assert not link2.exists()


def test_mk_symlinks_sets(tmp_path, monkeypatch):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = Path(tmp_path)
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"
    dataset_root = _create_dataset(tmp_path)
    from card_identifier.dataset import DatasetManager

    dm = DatasetManager("pokemon")
    dm.mk_symlinks("sets")
    link = dataset_root / "symlinks" / "sets" / "s1" / "s1-c1" / "img1.png"
    assert link.is_symlink()
    assert link.resolve() == dataset_root / "s1" / "s1-c1" / "img1.png"
