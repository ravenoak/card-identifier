# ADR-0004: Use TCGdex as the card data source, behind an adapter

## Status
Accepted (2026-10-09)

## Context
The catalog reads cards through `pokemontcgsdk` from pokemontcg.io. Facts on 2026-10-09:

- The `pokemon-tcg-data` README says the API is "scheduled to be taken offline on March 1,
  2027" and calls it legacy. The home page says it is now part of Scrydex.
- `pokemontcgsdk` 3.4.0 was last released on 2021-12-21. It requires `legalities` and, in the
  embedded set, `printedTotal`, so it cannot parse cards from new sets such as `me55c`.
- The API returned HTTP 500 on every endpoint tried at 2026-10-10 06:00 UTC.
- Scrydex is the stated successor, with compatible ids. Its pricing page lists no free tier
  (Starter: $29 a month for 5,000 credits). Its terms bar redistributing or mirroring data and
  extracting datasets.
- TCGdex is free, needs no key, and its card database is MIT-licensed
  (`tcgdex/cards-database`, last commit 2026-10-06). Its set list held 220 sets and its card
  list 23,736 entries on 2026-10-09. A card record carries `regulationMark`, `legal.standard`,
  `legal.expanded` and `illustrator`. Images come at `high` (600x825 per its docs) and `low`.
- Set ids differ between the two sources: of 176 `pokemon-tcg-data` set ids, 126 exist in
  TCGdex. `sv1` to `sv9`, `me1` to `me5` and `me55c` do not (TCGdex uses `sv01`, `me01` and
  `30th-c`), and 18 shared ids disagree on card totals.
- The sources also disagree on facts. TCGdex `30th-c` matches `me55c` by release date
  (2026-09-16) and size (30 cards), but it lists the set as not Standard-legal, where the
  pokemontcg.io payload in `tests/conftest.py` says Legal. TCGdex pads card numbers
  (`30th-c-001`), so ids cannot be mapped by set and number alone.

## Decision
Use TCGdex as the primary source, through a `CardSource` adapter
([FR-101](../specs/catalog.md)). Use TCGdex card and set ids as canonical ids, and keep earlier
ids in `legacy_ids` ([FR-104, FR-105](../specs/catalog.md)). A spike confirms coverage and
the id crosswalk before the adapter is built (#77).

### Alternatives considered
- **`pokemon-tcg-data` static JSON.** Same schema as today and no key. Rejected as primary: it
  carries the legacy banner and may stop updating after the sunset.
- **Scrydex.** Official successor. Rejected: paid, and its terms bar extracting datasets, which
  is this project's use.
- **Source-agnostic only.** The adapter makes a later switch possible, so the choice does not
  need to be final.

## Consequences
- The pipeline outlives the 2027-03-01 sunset.
- Existing datasets use pokemontcg.io ids. Some change, so a migration renames directories
  from the `legacy_ids` lookup (#86).
- TCGdex publishes no rate limit that the research found. The adapter bounds concurrency and
  retries ([FR-109](../specs/catalog.md)).
- Image rights are unchanged: no source grants them ([intent.md](../intent.md) constraints).
- Image size differs from today. The generator normalizes scale
  ([FR-209](../specs/generation.md)).

## References
- https://github.com/PokemonTCG/pokemon-tcg-data
- https://scrydex.com/faq, https://scrydex.com/pricing, https://scrydex.com/terms
- https://tcgdex.dev/, https://github.com/tcgdex/cards-database
- [catalog.md](../specs/catalog.md)
