import logging
import pickle
from pathlib import Path

from card_identifier.dataset import generator

# Test when referenced images are missing


def test_build_work_missing_images(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = Path(tmp_path)
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"
    config.backgrounds_dir = config.data_root / "backgrounds"

    image_dir = config.images_dir / "pokemon"
    pickle_dir = config.data_root / "barrel" / "pokemon"
    image_dir.mkdir(parents=True)
    pickle_dir.mkdir(parents=True)

    with open(pickle_dir / "card_image_map.pickle", "wb") as fh:
        pickle.dump({"s1-c1": "s1-c1.png", "s2-c2": "s2-c2.png"}, fh)

    caplog.set_level(logging.ERROR)
    builder = generator.DatasetBuilder("pokemon", num_images=1)
    work = builder.build_work()

    assert work == []
    assert any(
        "image s1-c1.png does not exist" in record.message for record in caplog.records
    )
    assert any(
        "image s2-c2.png does not exist" in record.message for record in caplog.records
    )


# Test run() logging when build_work returns no work


def test_run_no_work_logs_warning(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = Path(tmp_path)
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"
    config.backgrounds_dir = config.data_root / "backgrounds"

    image_dir = config.images_dir / "pokemon"
    pickle_dir = config.data_root / "barrel" / "pokemon"
    image_dir.mkdir(parents=True)
    pickle_dir.mkdir(parents=True)

    # Reference a missing image
    with open(pickle_dir / "card_image_map.pickle", "wb") as fh:
        pickle.dump({"s1-c1": "s1-c1.png"}, fh)

    caplog.set_level(logging.WARNING)
    builder = generator.DatasetBuilder("pokemon", num_images=1)
    builder.run()

    assert any("no work items generated" in record.message for record in caplog.records)
