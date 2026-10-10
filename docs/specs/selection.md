# Spec: selection, builds and splits

A selection picks cards from the catalog. A build turns a selection into a dataset with a
manifest. A split says which variants train, validate and test.

Intent: outcome 3 (chosen subsets) in [intent.md](../intent.md).

## Selection file

A TOML file. Every key is optional. A card is selected when it matches every key present
(include keys combine with AND across keys and OR within a key), and then none of the
`exclude` keys.

```toml
[select]
sets = ["swsh3", "swsh4"]        # canonical set ids
series = ["Sword & Shield"]
formats = ["standard"]           # "standard", "expanded"; card must be legal in all listed
regulation_marks = ["H", "I"]
rarity = ["Rare Holo"]
category = ["Pokemon"]
types = ["Fire"]
released_after = "2022-01-01"
cards = ["swsh3-136"]            # exact ids
id_glob = "sv0*-*"               # shell-style pattern over card ids

[exclude]
sets = ["swsh35"]
cards = []
```

Examples the format must express: one set, one series, only the cards legal in Standard today,
all Fire Pokemon in Standard, everything released since 2022 except one set.

## Build manifest

`builds/<name>/manifest.json`. Variant images live in the shared pool of FR-307:

| Field | Meaning |
|---|---|
| `schema_version` | Starts at 1 |
| `name`, `created_at` | Build name, UTC timestamp |
| `game` | `pokemon` |
| `selection` | The selection file contents and the resolved list of card ids |
| `catalog_hash` | Hash of `cards.jsonl` when the build resolved the selection |
| `seed` | Build seed (see FR-204) |
| `generator_config` | The generator config and its hash |
| `images_per_card` | Target number of variants per card |
| `code_version` | Git commit of this package, or the package version if not a checkout |
| `splits` | Split strategy, fractions and assignment (FR-308) |
| `counts` | Cards, variants, failures |
| `files` | For each variant: path, SHA-256, split |

## Requirements

**FR-301.** THE SYSTEM SHALL accept a selection file with the keys of the selection file example and SHALL reject an
unknown key with an error that names it.
*Check:* parametrized tests cover each key, and a typo such as `regulation_mark` fails.

**FR-302.** THE SYSTEM SHALL decide format legality per card from the card's `legal_standard`
and `legal_expanded` flags, and SHALL NOT infer a card's legality from its set.
*Check:* in a fixture set that holds one rotated card and one legal card, `formats =
["standard"]` selects only the legal card.

**FR-303.** WHEN a selected format needs a legality flag that is null for some cards, THE
SYSTEM SHALL leave those cards out, print how many it left out, and fail instead when
`--strict` is set.
*Check:* a fixture with 3 null cards prints "3 cards excluded: legality unknown".

**FR-304.** THE SYSTEM SHALL provide `select --dry-run`, which resolves a selection against
the catalog and prints the card count, the count per set and the total variants for a given
`images_per_card`, and writes nothing.
*Check:* on a fixture catalog the printed counts equal hand-computed values, and the command
runs with a read-only data root.

**FR-305.** THE SYSTEM SHALL provide `build`, which takes a selection, a generator config, a
seed and `images_per_card`, generates the missing variants, and writes a manifest.
*Check:* an end-to-end test over 3 fixture cards produces 3 times N images and one manifest.

**FR-306.** THE SYSTEM SHALL record in the manifest every field of the build manifest table.
*Check:* a schema test validates the manifest, and a second build from the manifest's own
inputs yields the same `files` list.

**FR-307.** THE SYSTEM SHALL store variants in a pool keyed by generator-config hash and
seed, and let builds reference them, so builds that share a card, a seed and a config share its
files.
*Check:* two overlapping builds with one seed and config hold the shared card's variants once
on disk. A build with another config does not reuse them.

**FR-308.** THE SYSTEM SHALL assign each variant to `train`, `val` or `test` in the manifest,
using one of two strategies: `per_card`, which splits each card's variants by fraction, and
`by_set`, which holds out whole sets for `val` and `test`. The default is `per_card` at
0.8, 0.1, 0.1.
*Check:* over 10,000 variants, the share in each split under `per_card` is within 2 points of
the configured fraction. Under `by_set` no set appears in two splits.

**FR-309.** THE SYSTEM SHALL assign splits from a hash of the seed and the variant's identity,
so adding cards or variants never moves an existing variant to a different split.
*Check:* building 100 cards, then 120, leaves the first 100 cards' assignments unchanged.

**FR-310.** THE SYSTEM SHALL provide `export-imagefolder`, which writes a
class-per-directory tree of symlinks to a path outside the build's image directory, for tools
that expect that layout.
*Check:* running `export-imagefolder` twice gives the same tree. No directory in the tree is named
`symlinks`, `all`, `legal` or `sets`.

**FR-311.** THE SYSTEM SHALL write a statistics report for a build, as JSON and Markdown, with
cards and variants per set, per rarity and per category, variants per card (minimum, median,
maximum), the use count of every transform step, the background mix, and failures.
*Check:* the report for a fixture build matches counts computed independently in the test.

**FR-312.** THE SYSTEM SHALL count a variant once when it scans a build, whatever links or
exports point at it.
*Check:* a build with an exported tree reports the same counts before and after export.

**FR-313.** THE SYSTEM SHALL describe card id filters as exact ids or a shell-style glob
(`id_glob`), and SHALL remove the `--str-filter` option that claims to match a substring while
matching a prefix.
*Check:* `--str-filter` is gone from `create-dataset --help`. `id_glob = "swsh3-*"` selects
the set.

## Current state and gaps

What exists:

- `DatasetManager.mk_symlinks(mode)` builds `symlinks/{all,legal,sets}` inside the dataset
  directory. It also treats `symlinks/` as a set from the first run, creating an empty class
  directory named after the mode (`symlinks/all/all`), and `scan_dataset_dir` then counts
  linked images twice under the card id `all` (#81).
- `legal` mode unions the Standard and Expanded sets from the live API. Standard legality
  follows a card's regulation mark (H, I and J cards are legal after the April 2026
  rotation, per one news source that still needs an official one), and sets without legality data drop out (#87).
- `create-dataset --str-filter` documents a substring and matches a prefix of the card id
  (#89).
- No manifest, no splits, no statistics (#90,
  #93).

| Requirement | Closed by |
|---|---|
| FR-301, FR-304, FR-313 | #89 |
| FR-302, FR-303 | #87 |
| FR-305 to FR-310 | #90 |
| FR-312 | #81 |
| FR-311 | #93 |
