from pokemontcgsdk.restclient import RestClient

from card_identifier.cards import pokemon

NEW_SET = {
    "id": "me55c",
    "name": "30th Celebration: Classic Collection",
    "series": "Mega Evolution",
    "total": 30,
    "legalities": {"unlimited": "Legal", "standard": "Legal", "expanded": "Legal"},
    "ptcgoCode": "30C",
    "releaseDate": "2026/09/16",
    "updatedAt": "2026/09/14 15:00:00",
    "images": {
        "symbol": "https://images.scrydex.com/pokemon/me55c-symbol/symbol",
        "logo": "https://images.scrydex.com/pokemon/me55c-logo/logo",
    },
}


def test_get_legal_sets_cached(monkeypatch):
    pokemon.get_legal_sets.cache_clear()

    calls = []

    def fake_get(url, params):
        calls.append((params["q"], params["page"]))
        if params["page"] > 1:
            return {"data": []}
        # The API returns new sets such as me55c without printedTotal.
        return {"data": [{**NEW_SET, "id": f"{params['q']}-id"}]}

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
