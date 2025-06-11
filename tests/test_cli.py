from click.testing import CliRunner

from card_identifier.cli.main import cli


def test_mkdataset_cli_dispatch(monkeypatch):
    called = {}

    def fake_create(num, card_type, id_filter=None):
        called["args"] = (num, card_type, id_filter)

    monkeypatch.setattr(
        "card_identifier.cli.create_dataset.create_random_training_images", fake_create
    )

    runner = CliRunner()
    result = runner.invoke(
        cli, ["create-dataset", "-n", "5", "-t", "pokemon", "-f", "s1"]
    )
    assert result.exit_code == 0, result.output
    assert called["args"] == (5, "pokemon", "s1")


def test_card_data_cli(tmp_path, monkeypatch):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = tmp_path
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"

    calls = {}

    class DummyCardManager:
        def __init__(self):
            calls["cm"] = self
            self.card_data = {"c1": object()}

        def refresh_data(self):
            calls["refresh"] = True

    class DummyImageManager:
        def __init__(self):
            pass

        def download_card_images(self, cards, force):
            calls["download"] = (list(cards), force)

        def refresh_card_image_map(self):
            calls["refresh_map"] = True

    monkeypatch.setattr(
        "card_identifier.cli.card_data.pokemon.CardManager",
        DummyCardManager,
    )
    monkeypatch.setattr(
        "card_identifier.cli.card_data.pokemon.ImageManager",
        DummyImageManager,
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["card-data", "--refresh", "--images", "--force"])
    assert result.exit_code == 0, result.output
    assert calls["refresh"]
    assert calls["download"][1] is True
    assert calls["refresh_map"]


def test_trim_dataset_cli(tmp_path, monkeypatch):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = tmp_path
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"

    dataset_root = config.datasets_dir / "pokemon"
    (dataset_root / "s1" / "s1-c1").mkdir(parents=True)
    (dataset_root / "s2" / "s2-c2").mkdir(parents=True)
    for i in range(3):
        for path in [dataset_root / "s1" / "s1-c1", dataset_root / "s2" / "s2-c2"]:
            (path / f"img{i}.png").write_bytes(b"x")

    called = {}

    def fake_load_random_state(path):
        called["pickle"] = path

    monkeypatch.setattr(
        "card_identifier.cli.trim_dataset.load_random_state",
        fake_load_random_state,
    )
    monkeypatch.setattr(
        "card_identifier.cli.trim_dataset.random.shuffle",
        lambda x: None,
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["trim-dataset", "-n", "1"])
    assert result.exit_code == 0, result.output
    assert len(list((dataset_root / "s1" / "s1-c1").glob("*.png"))) == 1
    assert len(list((dataset_root / "s2" / "s2-c2").glob("*.png"))) == 1
    assert called["pickle"] == tmp_path / "barrel" / "pokemon"


def test_save_random_state_cli(tmp_path, monkeypatch):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    from card_identifier.config import config

    config.data_root = tmp_path
    config.images_dir = config.data_root / "images" / "originals"
    config.datasets_dir = config.data_root / "images" / "dataset"

    called = {}

    def fake_save(path):
        called["path"] = path

    monkeypatch.setattr(
        "card_identifier.cli.random_state.save_state",
        fake_save,
    )

    seed = {}

    def fake_seed(value=None):
        seed["val"] = value

    monkeypatch.setattr(
        "card_identifier.cli.random_state.random.seed",
        fake_seed,
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["save-random-state", "-s", "42"])
    assert result.exit_code == 0, result.output
    assert seed["val"] == 42
    assert called["path"] == tmp_path / "barrel" / "pokemon"
