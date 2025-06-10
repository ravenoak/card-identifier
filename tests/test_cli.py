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
