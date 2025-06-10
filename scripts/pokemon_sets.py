from pokemontcgsdk import Set


def main():
    targeted_sets = set((s.id for s in Set.where(q="legalities.standard:legal"))).union(
        set((s.id for s in Set.where(q="legalities.expanded:legal")))
    )

    for set_id in targeted_sets:
        print(set_id)


if __name__ == "__main__":
    main()
