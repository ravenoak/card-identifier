from card_identifier.dataset import DatasetManager
from tests.test_dataset_symlinks import _create_dataset


def test_scan_dataset_dir_deep_path(tmp_path, monkeypatch):
    deep_root = tmp_path / "some" / "deep" / "structure"
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(deep_root))
    from card_identifier.config import config

    config.data_root = deep_root
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"

    dataset_root = _create_dataset(deep_root)

    dm = DatasetManager("pokemon")
    result = dm.scan_dataset_dir()

    assert set(result.keys()) == {"s1-c1", "s2-c2"}
    assert result["s1-c1"]["num_img"] == 1
    assert dataset_root / "s1" / "s1-c1" / "img1.png" in result["s1-c1"]["img_paths"]
    assert result["s2-c2"]["num_img"] == 1
    assert dataset_root / "s2" / "s2-c2" / "img2.png" in result["s2-c2"]["img_paths"]
