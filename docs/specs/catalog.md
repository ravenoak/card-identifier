# Spec: catalog and image store

The catalog is the local record of every card and set, with the card labels the identifier can
report. The image store holds one reference scan per card. Both are filled from a card source
through an adapter.

Intent: outcome 1 (trusted card data) in [intent.md](../intent.md). Decisions:
[ADR 0004](../adr/0004-tcgdex-as-card-data-source.md),
[ADR 0005](../adr/0005-catalog-and-manifests-as-json-or-parquet.md).

## Card label record

One record per card. Fields marked optional may be null. A null is stored as null, never as
a missing key, so readers see a stable shape.

| Field | Type | Notes |
|---|---|---|
| `schema_version` | int | Starts at 1 |
| `id` | string | Canonical card id, for example `swsh3-136`. Matches `^[a-z0-9][a-z0-9._-]*$`, so it is safe as a file name |
| `game` | string | `pokemon` |
| `name` | string | |
| `set_id` | string | Canonical set id. Taken from the set record, never parsed from `id` |
| `number` | string | Collector number as printed, for example `136` or `TG05` |
| `category` | string | `Pokemon`, `Trainer` or `Energy` |
| `subtypes` | list of string | For example `Basic`, `Stage 1`, `Supporter` |
| `types` | list of string | Energy types. Empty for Trainer and Energy |
| `hp` | int, optional | |
| `rarity` | string, optional | As the source states it |
| `regulation_mark` | string, optional | A letter. Null for cards printed before marks existed |
| `legal_standard` | bool, optional | Null means unknown |
| `legal_expanded` | bool, optional | Null means unknown |
| `illustrator` | string, optional | |
| `image_url` | string, optional | Base URL of the source image |
| `legacy_ids` | list of string | Ids this card had in earlier sources, for example the pokemontcg.io id |
| `source` | string | Adapter name, for example `tcgdex` |
| `source_id` | string | The id in that source |
| `fetched_at` | string | UTC timestamp, ISO 8601 |

## Set record

| Field | Type | Notes |
|---|---|---|
| `schema_version` | int | |
| `id` | string | Canonical set id |
| `game` | string | |
| `name` | string | |
| `series` | string | |
| `release_date` | string | ISO date |
| `card_count` | int | Cards in the set as the source counts them |
| `legal_standard` | bool, optional | Informational only. Selection uses the card flags (FR-302) |
| `legal_expanded` | bool, optional | |
| `legacy_ids` | list of string | |
| `source`, `source_id`, `fetched_at` | | As for cards |

## Requirements

**FR-101.** THE SYSTEM SHALL read cards and sets from a source only through a `CardSource`
adapter, so that no module outside the adapter imports a source SDK or makes a source request.
*Check:* a test lists imports of `pokemontcgsdk`, `requests` and `urllib` outside
`sources/` and finds none.

**FR-102.** WHEN a source record omits an optional field, THE SYSTEM SHALL store the card with
that field null and SHALL NOT fail the fetch.
*Check:* a fixture card with no `hp`, `rarity`, `regulation_mark` or legality is stored with
nulls. A fixture for the 30th Celebration set (`me55c` in pokemontcg.io, `30th-c` in TCGdex), which
lacks several fields, loads.

**FR-103.** IF one record fails to parse, THEN THE SYSTEM SHALL log the source id and the
reason, continue with the remaining records, print the failure count at the end, and exit
non-zero.
*Check:* a fetch over three records with one malformed stores two, logs one error naming the
bad record, and exits 1.

**FR-104.** THE SYSTEM SHALL use the TCGdex card id as the canonical card id and the TCGdex
set id as the canonical set id.
*Check:* the crosswalk spike (#77) lists every id that differs from a
legacy id. The catalog holds no two cards with one canonical id.

**FR-105.** THE SYSTEM SHALL keep every earlier id of a card in `legacy_ids` and SHALL provide
a lookup from any legacy id to the canonical id.
*Check:* all card ids in an existing `card_image_map` resolve, or appear in a printed list of
unmapped ids. Existing dataset directories can be renamed from that lookup
(#86).

**FR-106.** THE SYSTEM SHALL store a card label record, as defined above, for every card the
source lists.
*Check:* a schema test validates each stored record, and a count test compares the catalog
with the source's card count.

**FR-107.** THE SYSTEM SHALL persist the catalog as plain files with `schema_version`, readable
without this package, and SHALL NOT persist it with pickle.
*Check:* a test loads `cards.jsonl` with only the standard library. `grep -r pickle
card_identifier/catalog` finds nothing.

**FR-108.** THE SYSTEM SHALL store a set record for every set the source lists.
*Check:* every `set_id` in the card file has a set record.

**FR-109.** WHEN a request fails with a network error, a timeout, HTTP 429 or HTTP 5xx, THE
SYSTEM SHALL retry with exponential backoff up to a configured limit, then record the failure
and continue.
*Check:* a fake server returning 500 twice and then 200 succeeds. One returning 500 forever
fails after the limit, with a failure in the summary.

**FR-110.** WHEN an image is downloaded, THE SYSTEM SHALL decode it with Pillow, check that
both sides are at least a configured minimum, and reject it otherwise without writing it to
the image store.
*Check:* a 200 response with an HTML body is rejected, logged and absent from `images.jsonl`.

**FR-111.** THE SYSTEM SHALL write catalog files and images to a temporary name in the same
directory and rename them into place, so a crash leaves either the old file or the new one.
*Check:* a test that raises during write leaves no partial target file.

**FR-112.** THE SYSTEM SHALL keep one image index, `images.jsonl`, with the file name, SHA-256,
width, height, source URL and fetch time of every reference scan, and SHALL rebuild it from the
image directory on request.
*Check:* deleting the index and running the rebuild command restores the same records.

**FR-113.** THE SYSTEM SHALL NOT perform network or disk-creating work when a manager object
is constructed.
*Check:* constructing the catalog and image managers with the network blocked and an empty
data root creates no files and makes no request.

**FR-114.** WHEN `card-data --refresh` runs on an empty data root, THE SYSTEM SHALL fetch each
resource once.
*Check:* a request counter over a cold refresh shows one pass over cards and one over sets.

**FR-115.** THE SYSTEM SHALL find games and their adapters through a registry, SHALL derive
the `--card-type` choices from it, and SHALL keep game-specific imports out of the core
modules.
*Check:* adding a stub game to the registry makes `--card-type stub` valid with no other code
edit. A test fails if a core module imports `card_identifier.games.pokemon`.

**FR-116.** WHEN an image is stored, THE SYSTEM SHALL record its source URL in the image index,
and THE SYSTEM SHALL keep `data/` out of git and out of container images.
*Check:* `.gitignore` and `.dockerignore` cover `data/`. The README states that images are
for local training and are not redistributed.

## Current state and gaps

What exists:

- `cards/pokemon/CardManager` fetches through `pokemontcgsdk` and pickles SDK objects.
  It fails on cards from new sets, because the SDK requires `legalities` and the embedded set's
  `printedTotal` (#76).
- `ImageManager` downloads `card.images.large` to `<id>.png` and pickles an id-to-file map.
  Downloads have no timeout on the SDK side, retry only HTTP 429, and accept any 200 body
  (#82).
- Two different files named `card_image_map.pickle` exist, one in `barrel/<game>/` and one in
  the dataset directory (#88).
- Constructors fetch over the network (#91).
- `data.NAMESPACES` is a hand-kept list and `card_data` dispatches with `if`
  (#92).
- The source goes offline on 2027-03-01 (#77,
  #85, #86).
- Image rights and background sourcing are undocumented (#98).

| Requirement | Closed by |
|---|---|
| FR-101, FR-102, FR-103, FR-109 | #85 |
| FR-104 | #77 |
| FR-105 | #86 |
| FR-106, FR-107, FR-108, FR-112 | #88 |
| FR-110, FR-111 | #82 |
| FR-113, FR-114 | #91 |
| FR-115 | #92 |
| FR-116 | #98 |
