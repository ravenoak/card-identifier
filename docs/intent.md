# Intent

This document replaces `DESIGN.md`. It says what card-identifier is for. The specs say how it
behaves, and the ADRs say why it is built that way.

## Purpose

Identify a physical trading card from a photograph, and tell the user what the card is. A
card has an identity (this exact print of Pikachu) and labels (set, name, rarity, type,
regulation mark, format legality). The first game is the Pokemon TCG. Magic: The Gathering and
Yu-Gi-Oh! come later.

Two parts serve that purpose:

1. **Dataset manager.** Fetch card data and one reference scan per card, then generate many
   randomized training images per card. Select which cards go into a dataset, for example one
   set, one series, or only the cards legal in the Standard format.
2. **Identifier.** Train a model on a selected dataset, evaluate it on real photographs, and
   use it to identify cards. Several model architectures are trainable and comparable.

A card sorting robot is the first consumer. Inventory, sorting and valuation tools follow.

## Why this approach

Only one clean scan exists per card, and there are about 20,000 Pokemon cards (20,530 in
pokemon-tcg-data, 23,964 in TCGdex, both on 2026-10-09). No labeled photo set exists. So the
project makes synthetic photos from the scans, trains on them, and measures on a small set of
real photos. New sets appear several times a year, so adding a set must not mean retraining
from scratch. [ADR 0003](adr/0003-retrieval-first-identification.md) records the answer:
compare embeddings against a reference index.

## Users

| User | What they do | What they need |
|---|---|---|
| Owner (subject-matter expert) | Builds datasets, trains and compares models, runs evaluations | Commands that run unattended, reproduce, and say what they did |
| Sorting robot (consumer) | Sends a camera frame, receives a card id and labels | A small self-contained model bundle and a stable `identify` contract |
| Future contributor | Adds a game, a model architecture or a transform | A clear extension point and a spec to write against |

## Outcomes

Each outcome names the specs that deliver it.

1. **Trusted card data.** A local catalog of every card and set, with labels, from a source
   that stays available. [catalog](specs/catalog.md)
2. **Believable synthetic photos.** Generated images that look like what a camera sees, with
   a record of every transform applied. [generation](specs/generation.md)
3. **Chosen subsets.** Any slice of the catalog becomes a named, reproducible dataset build.
   [selection](specs/selection.md)
4. **Comparable models.** More than one architecture trains from the same build and the same
   command. [training](specs/training.md)
5. **Honest numbers.** Accuracy is measured on real photographs, per label, and never on
   synthetic data alone. [evaluation](specs/evaluation.md)
6. **A usable identifier.** One command, or one exported bundle, turns a photo into a card
   and its labels. [inference](specs/inference.md)

## Proposed success measures

These targets are proposals. No baseline exists, because the pipeline has never run end to
end (see the [2026-10-09 examination](examinations/2026-10-09-critical-examination.md)).
The owner must confirm or replace them. Until then they guide design, and no issue is
blocked on them.

| Measure | Proposed target | Where measured |
|---|---|---|
| Top-1 card id accuracy, in-index cards, real photos | 95% or more | [evaluation](specs/evaluation.md) FR-502 |
| Top-5 card id accuracy, same set | 99% or more | FR-502 |
| Set accuracy, real photos | 99% or more | FR-502 |
| Two builds from the same inputs | Identical image hashes | FR-204 |
| Adding a new set to a trained system | No retraining, one command | FR-406 |
| Rebuilding a 1,000-card selection | Reports images per second, no failures | NFR-6 |

## Scope

In scope: Pokemon TCG, English cards, one card per photograph, training and evaluation on a
single machine, a command line and a Python library.

## Non-goals

- Finding or cropping a card inside a wide camera frame. The input is a photo that is mostly
  one card. Detection is a later project.
- Grading card condition or estimating price.
- A graphical interface. The Streamlit demo is an experiment and has no requirements.
- Cloud storage or Airflow integration. Local files only, with paths that a container can
  mount. Revisit when a use case exists.
- Distributed training.
- Redistributing card images or trained weights built from them. See the licensing note
  below.
- Games other than Pokemon until the Pokemon pipeline has a measured baseline.

## Constraints

- One developer and a small budget. Prefer free data sources and free tools.
- Code is AGPL-3.0-or-later. Pretrained model weights carry their own licences, and some
  forbid commercial use. Each backbone records its licence ([FR-403](specs/training.md)).
- Card artwork belongs to its owners. No source reviewed grants rights to the images
  (Scrydex terms bar redistributing and extracting datasets, and TCGdex licenses its database,
  not the artwork). The project downloads images for the owner's own training, keeps them out
  of git and out of container images, and does not publish them.
- Python 3.13 and 3.14. PyTorch supports both. TensorFlow has no 3.14 wheels
  ([ADR 0002](adr/0002-pytorch-and-timm-for-training.md)).

## Glossary

| Term | Meaning |
|---|---|
| Game | A trading card game. `pokemon` today. Also called a namespace in the code |
| Card | One printed card, identified by its canonical card id, for example `swsh3-136` |
| Print | The same card printed in another set or as another variant. Each print is its own card id |
| Set | A release of cards, for example `swsh3`. A set belongs to a series |
| Series | A group of sets, for example Sword & Shield |
| Regulation mark | The letter printed on a card (D, E, F, G, H, I, J) that decides Standard legality |
| Format legality | Whether a card is legal in Standard or Expanded play, stored per card |
| Card label | An attribute of a card that the system can report: set, name, rarity, category, types, regulation mark, legality. Not a GitHub label |
| Catalog | The local, versioned record of every card and set with its card labels |
| Reference scan | The one clean image per card downloaded from the source |
| Variant | One generated training image made from a reference scan |
| Selection | A declarative filter over the catalog that picks cards |
| Build | A named dataset made from a selection, a generator config, a seed and a count per card, described by a manifest |
| Manifest | The JSON file that records everything needed to reproduce a build |
| Backbone | A pretrained image network (for example a ViT or a ConvNeXt) used as the base of a model |
| Embedding | A vector the model produces for an image. Images of the same card land close together |
| Reference index | The embeddings of every reference scan, searched by cosine similarity to identify a photo |
| Real-photo set | Photographs of physical cards with known card ids, used only to evaluate |

## Open decisions for the owner

- Confirm or replace the proposed success measures above.
- Decide ADR 0005 (catalog and manifest file formats) and ADR 0006 (offline plus online
  augmentation). Both are Proposed.
- Decide how the real-photo set is collected and how many cards it covers
  ([FR-501](specs/evaluation.md)).
