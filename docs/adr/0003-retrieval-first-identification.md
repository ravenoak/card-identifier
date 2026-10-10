# ADR-0003: Identify cards by embedding retrieval, with a classifier as baseline

## Status
Accepted (2026-10-09)

## Context
The task is to identify one of about 20,000 cards from a photo. Each card has one clean scan
and no real photos. New sets appear several times a year. The owner also wants labels beyond
the card id (set, rarity, type, regulation mark).

A softmax classifier over card ids has one output per card, so it must be retrained when a set
is added, and each class has few real examples. Retrieval compares an embedding of the photo
with embeddings of the reference scans. Two public projects use that approach on card games:
`LMilazzo/cardexx` (CLIP ViT-B/16 embeddings, cosine match against about 19,000 Pokemon
reference images) and `ManuelZ/pairwise-similarity` (Magic: The Gathering, one image per card,
Circle Loss, similarity search). Both were read on 2026-10-09 through their READMEs.

## Decision
Make retrieval the primary method. A backbone plus an embedding head is trained with a
metric-learning loss on synthetic variants. The system embeds every reference scan into an
index and answers a photo with its nearest neighbours by cosine similarity. Every card label
comes from the catalog record of the matched card. Keep a softmax classifier head as a
selectable baseline, so the two methods compare on the same data and photos
(#107).

## Consequences
- Adding a set means embedding its scans and appending vectors. No retraining
  ([FR-406](../specs/training.md)).
- Labels never drift from the catalog, because they are looked up, not predicted. Auxiliary
  attribute heads stay optional ([FR-408](../specs/training.md)).
- The index must match the model that built it. The index stores the model hash and refuses a
  mismatch ([FR-405](../specs/training.md)).
- Brute-force cosine search over about 25,000 vectors is enough. Add an approximate index only
  after a measurement shows a need.
- The method depends on how well synthetic variants stand in for photos. Real-photo
  evaluation decides, not synthetic validation ([FR-505](../specs/evaluation.md)).

## References
- [training.md](../specs/training.md), [evaluation.md](../specs/evaluation.md)
- https://github.com/LMilazzo/cardexx
- https://github.com/ManuelZ/pairwise-similarity
