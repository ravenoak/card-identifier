import streamlit as st

from card_identifier import pokemon


st.title('Card Identifier')
collection_type = st.sidebar.selectbox('Collection Type', ['Pokemon'])

cards = pokemon.get_card_data()
card_sets = pokemon.get_set_data()

card_set = st.sidebar.selectbox(
    'Card Set',
    card_sets,
    format_func=lambda s: f'{s.series}: {s.name}')
st.image(card_set.logo_url, width=200)

set_cards = cards[card_set.code]
set_cards.sort(key=lambda c: int(c.number))
card = st.sidebar.selectbox('Card', set_cards, format_func=lambda c: c.id)
st.image(card.image_url, width=500)
