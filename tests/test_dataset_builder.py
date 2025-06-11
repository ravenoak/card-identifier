import json
from pathlib import Path

from PIL import Image

from card_identifier.dataset import generator


def test_dataset_builder_run(tmp_path, monkeypatch):
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

    img1 = image_dir / "s1-c1.png"
    img2 = image_dir / "s2-c2.png"
    Image.new("RGB", (10, 10), color=(255, 0, 0)).save(img1)
    Image.new("RGB", (10, 10), color=(0, 255, 0)).save(img2)

    with open(pickle_dir / "card_image_map.pickle", "wb") as fh:
        import pickle

        pickle.dump({"s1-c1": "s1-c1.png", "s2-c2": "s2-c2.png"}, fh)

    monkeypatch.setattr(
        generator.background, "BACKGROUND_TYPES", ["random_solid_color"]
    )
    monkeypatch.setattr(
        generator,
        "func_map",
        {"random_solid_color": generator.background.random_solid_color},
    )
    monkeypatch.setattr(
        generator.transformers,
        "random_perspective_transform",
        lambda img, wobble_percent=0.2: (img, {}),
    )

    class DummyPool:
        def __init__(self, processes=None):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def starmap(self, func, work):
            for args in work:
                func(*args)

    monkeypatch.setattr(generator.mp, "Pool", DummyPool)
    monkeypatch.setattr(generator.mp, "set_start_method", lambda *a, **k: None)

    builder = generator.DatasetBuilder("pokemon", num_images=1)
    builder.run()

    dataset_dir = config.datasets_dir / "pokemon"
    for card_id in ["s1-c1", "s2-c2"]:
        card_dir = dataset_dir / card_id.split("-")[0] / card_id
        images = list(card_dir.glob("*.png"))
        metas = list(card_dir.glob("*.json"))
        assert len(images) == 1
        assert len(metas) == 1
        meta = json.loads(metas[0].read_text())
        assert meta["filename"] == images[0].name
        assert "details" in meta


def test_dataset_builder_build_work(tmp_path, monkeypatch):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = Path(tmp_path)
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"
    config.backgrounds_dir = config.data_root / "backgrounds"

    image_dir = config.images_dir / "pokemon"
    pickle_dir = config.data_root / "barrel" / "pokemon"
    dataset_root = config.datasets_dir / "pokemon"

    image_dir.mkdir(parents=True)
    pickle_dir.mkdir(parents=True)
    dataset_root.mkdir(parents=True)

    img1 = image_dir / "s1-c1.png"
    img2 = image_dir / "s2-c2.png"
    Image.new("RGB", (10, 10), color=(255, 0, 0)).save(img1)
    Image.new("RGB", (10, 10), color=(0, 255, 0)).save(img2)

    with open(pickle_dir / "card_image_map.pickle", "wb") as fh:
        import pickle

        pickle.dump({"s1-c1": "s1-c1.png", "s2-c2": "s2-c2.png"}, fh)

    existing_dir = dataset_root / "s2" / "s2-c2"
    existing_dir.mkdir(parents=True)
    (existing_dir / f"old1.{generator.DEFAULT_OUT_EXT}").write_bytes(b"1")
    (existing_dir / f"old2.{generator.DEFAULT_OUT_EXT}").write_bytes(b"2")

    builder = generator.DatasetBuilder("pokemon", num_images=3, id_filter="s2")
    work = builder.build_work()

    assert len(work) == 1
    original, save_path, save_num = work[0]
    assert original == image_dir / "s2-c2.png"
    assert save_path == existing_dir
    assert save_num == 1
    assert not (dataset_root / "s1" / "s1-c1").exists()
