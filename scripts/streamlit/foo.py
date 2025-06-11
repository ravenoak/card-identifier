import streamlit as st

from card_identifier.cards import pokemon

st.title("Card Identifier")
collection_type = st.sidebar.selectbox("Collection Type", ["Pokemon"])

cm = pokemon.CardManager()

card_set = st.sidebar.selectbox(
    "Card Set", cm.set_data.values(), format_func=lambda s: f"{s.series}: {s.name}"
)
st.image(card_set.logo_url, width=200)

set_cards = cm.set_card_map[card_set.id]
set_cards.sort(key=lambda c: int(c.number))
card = st.sidebar.selectbox("Card", set_cards, format_func=lambda c: c.id)
st.image(card.image_url, width=500)
