#!/usr/bin/env python3
from card_identifier.cards.pokemon import get_legal_sets


def main():
    for set_id in get_legal_sets():
        print(set_id)


if __name__ == "__main__":
    main()
