import pytest


@pytest.fixture
def new_set() -> dict:
    """A set as the API returns it for new sets: no ``printedTotal``."""
    return {
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
