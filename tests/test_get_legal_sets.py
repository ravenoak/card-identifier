from types import SimpleNamespace

from card_identifier.cards import pokemon


def test_get_legal_sets_cached(monkeypatch):
    pokemon.get_legal_sets.cache_clear()

    calls = []

    def fake_where(q):
        calls.append(q)
        return [SimpleNamespace(id=f"{q}-id")]

    monkeypatch.setattr("pokemontcgsdk.Set.where", fake_where)

    result1 = pokemon.get_legal_sets()
    result2 = pokemon.get_legal_sets()

    assert result1 == {
        "legalities.standard:legal-id",
        "legalities.expanded:legal-id",
    }
    assert result1 is result2
    assert calls == ["legalities.standard:legal", "legalities.expanded:legal"]
