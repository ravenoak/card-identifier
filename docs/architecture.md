# Architecture

This document shows the system as it is today and as the specs make it. Status words:
**exists**, **partial** and **planned**.

## Component map

```
 card source (TCGdex)            backgrounds
        |                             |
        v                             v
  [catalog] ---> [image store] ---> [generator] ---> variants + sidecars
   cards, sets     reference scans      |
        |                               v
        +--------------------->  [selection + builds] ---> manifest
                                        |
                                        v
                                   [trainer] ---> checkpoint
                                        |
                                        v
                                [reference index] <--- reference scans
                                        |
                       +----------------+----------------+
                       v                                 v
                 [evaluation]                     [inference + export]
                 real-photo set                   identify CLI, ONNX bundle
```

| Component | Spec | Today |
|---|---|---|
| Catalog (cards, sets, card labels) | [catalog](specs/catalog.md) | **Partial.** `cards/pokemon` pickles SDK objects from pokemontcg.io |
| Image store (reference scans) | [catalog](specs/catalog.md) | **Partial.** `ImageManager` downloads PNGs and pickles an id-to-file map |
| Generator (transform chain) | [generation](specs/generation.md) | **Partial.** `dataset/generator.py` and `image/`. Fails on the sidecar write |
| Selection and builds | [selection](specs/selection.md) | **Partial.** Three symlink modes in `DatasetManager.mk_symlinks`. No manifest or splits |
| Trainer | [training](specs/training.md) | **Planned.** Notebooks and a removed TF Hub script only |
| Reference index | [training](specs/training.md) | **Planned** |
| Evaluation | [evaluation](specs/evaluation.md) | **Planned** |
| Inference and export | [inference](specs/inference.md) | **Planned.** `scripts/label_image.py` is a TFLite sample |

## Code layout

Today:

```
card_identifier/
  cards/base.py            BaseCardManager (abstract)
  cards/pokemon/           CardManager, ImageManager, api_client (pokemontcgsdk)
  dataset/                 DatasetManager (symlinks), generator (DatasetBuilder)
  image/                   transformers, background, meta
  cli/                     card-data, create-dataset, trim-dataset, save-random-state
  config.py, data.py       paths from CARDIDENT_* variables
  storage.py, util.py      pickle helpers, HTTP session, logging
```

Target (names are proposals; the specs bind behavior, not module names):

```
card_identifier/
  games/                   registry; games/pokemon/ holds the adapter, legality rule, label extras
  catalog/                 schema, store, image index, CardSource protocol, sources/tcgdex.py
  generate/                transform chain, config, backgrounds, sidecar schema, builder
  select/                  selection language, builds, manifest, splits, export, stats
  train/                   backbone registry, loader, losses, loops, checkpoints
  index/                   reference index build, add, search
  evaluate/                real-photo protocol, metrics, reports
  infer/                   preprocess, identify, ONNX export
  cli/                     one command group per stage
```

The package keeps its name. Moves happen under the issues that need them, never in a bulk
rename.

## Data layout

All data lives under `CARDIDENT_DATA_ROOT` (default `data`). Nothing under it is committed or
copied into a container image. The file formats follow ADR 0005 and ADR 0006, both Proposed.

```
data/
  catalog/<game>/
    cards.jsonl            one card label record per line (FR-106, FR-107)
    sets.jsonl             one set record per line (FR-108)
    images.jsonl           reference scan index: file, sha256, size, source URL (FR-112)
  images/originals/<game>/<card-id>.png      reference scans
  backgrounds/                               owner-supplied background images
  variants/<config-hash>-<seed>/<set-id>/<card-id>/<hash>.png     shared pool (FR-307), with <hash>.json sidecars
  builds/<name>/
    manifest.json          selection, seed, config hash, code version, counts (FR-306)
    config.toml            generator config used
  runs/<name>/
    config.toml, metrics.jsonl, checkpoints/, model-card.json      (FR-411)
  indexes/<name>/
    embeddings.npy, ids.json, index.json     (FR-405)
  eval/<set-name>/
    photos/, labels.csv                      real-photo set (FR-501)
  reports/                                   evaluation reports (FR-503)
```

Today the data root holds `images/originals`, `images/dataset` and `barrel/<game>` pickles.
[ADR 0005](adr/0005-catalog-and-manifests-as-json-or-parquet.md) (Proposed) covers the move.

## Trust boundaries

| Boundary | Untrusted input | Control |
|---|---|---|
| Card source API | JSON payloads, image bytes, URLs | Timeout and bounded retry (NFR-4). Parse per card, so one bad record does not fail the fetch (FR-103). Validate image decode and size (FR-110, NFR-7) |
| Downloaded images | Pixel data, dimensions, file names | Pillow decode with a pixel limit. File names come from validated card ids only (NFR-7) |
| Backgrounds directory | Any file the owner drops there | Skip non-images with a warning (FR-210) |
| Pretrained weights | Files from the Hugging Face Hub | Load safetensors, not pickle. Record source, revision and licence (FR-402, FR-403) |
| Persisted state | Files from an older run or another machine | Plain formats with `schema_version` (NFR-3). Never unpickle |
| Real photos | Camera files | Decode as RGB, apply orientation, reject non-images (FR-605) |

## Cross-cutting design

- **Configuration.** Paths come from `CARDIDENT_*` variables, read once at import today. The
  target reads them once into an object that tests can replace. Behavior settings (transform
  ranges, training schedule) live in TOML files that a manifest or run copies.
- **Concurrency.** Generation uses a `spawn` process pool. Each task takes everything it needs
  as arguments, including its seed, so workers share no state (FR-204).
- **Logging.** Workers rebuild logging from `CARDIDENT_DEBUG` because `spawn` does not inherit
  it. This works today and stays.
- **Errors.** Commands collect per-item failures, print a summary and exit 1 when any
  occurred (FR-103, FR-211).

## Decisions

[ADR index](adr/): 0001 record decisions, 0002 PyTorch and timm, 0003 retrieval first,
0004 TCGdex source, 0005 catalog and manifest formats (Proposed), 0006 offline plus online
augmentation (Proposed).
