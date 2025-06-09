from types import SimpleNamespace

import pytest

from card_identifier.cards import pokemon


class MockClient:
    def __init__(self):
        self.cards = [
            SimpleNamespace(id="c1", set=SimpleNamespace(id="s1")),
            SimpleNamespace(id="c2", set=SimpleNamespace(id="s2")),
        ]
        self.sets = [SimpleNamespace(id="s1"), SimpleNamespace(id="s2")]

    def iter_cards(self):
        return list(self.cards)

    def iter_sets(self):
        return list(self.sets)


def test_card_manager_uses_api_client(tmp_path, monkeypatch):
    monkeypatch.setenv("CARDIDENT_DATA_ROOT", str(tmp_path))
    cm = pokemon.CardManager(api_client=MockClient())

    assert set(cm.card_data.keys()) == {"c1", "c2"}
    assert set(cm.set_data.keys()) == {"s1", "s2"}
    assert cm.set_card_map == {"s1": ["c1"], "s2": ["c2"]}
