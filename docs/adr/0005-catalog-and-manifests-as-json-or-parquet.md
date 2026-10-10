# ADR-0005: Store the catalog, manifests and indexes in plain formats

## Status
Proposed (2026-10-09)

## Context
State today is pickle: SDK card and set objects (`cards.pickle`, `sets.pickle`), id maps, and
the random state (`storage.py:10-23`). A pickle ties the data to class definitions, so a new
SDK version or a moved class breaks old files. Loading one runs code. Two different files share
the name `card_image_map.pickle`, one in `barrel/<game>/` and one in the dataset directory.

The catalog holds about 24,000 cards with about 20 fields.

## Decision (proposed)
- Catalog: JSON Lines (`cards.jsonl`, `sets.jsonl`, `images.jsonl`), one record per line, with
  `schema_version`. The standard library reads it, and a diff shows what changed.
- Manifest and sidecars: JSON.
- Reference index: NumPy `.npy` for vectors and JSON for ids and metadata.
- Reconsider Parquet only if a measurement shows JSON Lines is too slow to load. At 24,000
  records it is not expected to be.
- A one-time reader may load old pickles to migrate them. It is the only pickle use
  ([NFR-3](../specs/nfr.md)).

### Alternatives considered
- **SQLite.** Good for queries. Rejected for now: selection runs in memory over 24,000 cards,
  and files are easier to inspect and diff.
- **Parquet.** Compact and typed, but needs a dependency and is not human-readable.

## Consequences
- Old `barrel/` data needs migration, and the migration reader keeps one pickle use alive for
  one release.
- Adding a field means bumping `schema_version` and writing a reader for the old version.

## References
- [catalog.md](../specs/catalog.md) FR-106 to FR-108, FR-112
- [selection.md](../specs/selection.md) FR-306
