from pokemontcgsdk.restclient import RestClient

from card_identifier.cards.pokemon.api_client import PokemonTCGSDKClient


def test_iter_sets_accepts_set_without_printed_total(monkeypatch, new_set):
    def fake_get(url, params):
        return {"data": [new_set] if params["page"] == 1 else []}

    monkeypatch.setattr(RestClient, "get", staticmethod(fake_get))

    sets = list(PokemonTCGSDKClient().iter_sets())

    assert [s.id for s in sets] == ["me55c"]
    assert sets[0].printedTotal is None
    assert (sets[0].series, sets[0].name) == (
        "Mega Evolution",
        "30th Celebration: Classic Collection",
    )
