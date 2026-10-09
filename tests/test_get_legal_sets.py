from pokemontcgsdk.restclient import RestClient

from card_identifier.cards import pokemon


def test_get_legal_sets_cached(monkeypatch, new_set):
    pokemon.get_legal_sets.cache_clear()

    calls = []

    def fake_get(url, params):
        calls.append((params["q"], params["page"]))
        if params["page"] > 1:
            return {"data": []}
        # The API returns new sets such as me55c without printedTotal.
        return {"data": [{**new_set, "id": f"{params['q']}-id"}]}

    monkeypatch.setattr(RestClient, "get", staticmethod(fake_get))

    result1 = pokemon.get_legal_sets()
    result2 = pokemon.get_legal_sets()

    assert result1 == {
        "legalities.standard:legal-id",
        "legalities.expanded:legal-id",
    }
    assert result1 is result2
    assert calls == [
        ("legalities.standard:legal", 1),
        ("legalities.standard:legal", 2),
        ("legalities.expanded:legal", 1),
        ("legalities.expanded:legal", 2),
    ]
