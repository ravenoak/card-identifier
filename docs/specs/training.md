# Spec: training and reference index

The trainer fits a model on a build. The reference index lets the model identify cards by
nearest neighbour. Several backbones and two heads (embedding and classifier) are selectable
by config.

Intent: outcome 4 (comparable models) in [intent.md](../intent.md). Decisions:
[ADR 0002](../adr/0002-pytorch-and-timm-for-training.md) (PyTorch and timm),
[ADR 0003](../adr/0003-retrieval-first-identification.md) (retrieval first).

## How identification works

1. A backbone maps an image to a feature vector. An embedding head projects it to a
   normalized vector.
2. Training pulls variants of one card together and pushes different cards apart, using the
   build's `train` split.
3. After training, the system embeds the clean reference scan of every card and stores the
   vectors as the reference index.
4. To identify a photo, the system embeds it and finds the nearest vectors by cosine
   similarity. The best match is the card id. Every other card label comes from the catalog
   record of that card.

Adding a set needs new reference vectors and no training (FR-406). The classifier head is a
baseline: a softmax over card ids on the same data, which needs retraining for each new set.

## Run config

A TOML file, copied into the run directory:

```toml
[data]
manifest = "builds/swsh/manifest.json"

[model]
backbone = "vit_small_patch14_dinov2"   # a registry name
head = "embedding"                      # "embedding" or "classifier"
embedding_dim = 256
freeze_backbone_epochs = 2

[train]
loss = "arcface"
epochs = 30
batch_size = 64
lr = 3e-4
seed = 1312
device = "auto"                         # "auto", "cuda", "mps", "cpu"

[augment]
online = true                           # see ADR 0006
```

The backbone name and loss shown are examples. The registry decides what exists.

## Requirements

**FR-401.** THE SYSTEM SHALL provide `train`, which takes a run config, and SHALL stop before
training when the manifest is missing or a sampled file's SHA-256 differs from the manifest.
*Check:* a test with a tampered file stops with a message naming the file.

**FR-402.** THE SYSTEM SHALL keep a backbone registry in which each entry holds the registry
name, the timm model name, the pretrained weight tag, the input size, the normalization mean
and standard deviation, the weight source and the weight licence, and adding a backbone SHALL
need only a new entry.
*Check:* a test adds a toy entry and trains one step on it with no other code change.

**FR-403.** WHEN a backbone's weight licence is unknown or forbids commercial use, THE SYSTEM
SHALL stop and ask for `--accept-licence`, and SHALL record the accepted licence in the run
metadata.
*Check:* an entry marked `cc-by-nc-4.0` stops without the flag, runs with it, and the run's
`model-card.json` names the licence.

**FR-404.** WHEN the head is `embedding`, THE SYSTEM SHALL train an embedding on the `train`
split with a metric-learning loss chosen in the config, SHALL support a schedule that freezes
the backbone for the first epochs, and SHALL compute a validation metric each epoch.
*Check:* a 2-epoch run on 20 fixture cards lowers the training loss and writes a metric per
epoch.

**FR-405.** THE SYSTEM SHALL build a reference index by embedding one reference scan per card
in the build, store the vectors and ids in plain files, record the model hash in the index,
and answer a query with the top-k card ids by cosine similarity.
*Check:* querying a reference scan returns its own id at rank 1. A query against an index built
by a different model is refused.

**FR-406.** WHEN cards are added to the catalog, THE SYSTEM SHALL add their vectors to an
existing index with `index add`, and SHALL NOT retrain.
*Check:* an index over 10 cards gains 5 more, and the first 10 vectors are unchanged.

**FR-407.** WHEN the head is `classifier`, THE SYSTEM SHALL train a softmax over the build's
card ids with the same loader, backbone registry, seed handling and run layout, and SHALL
write a label map.
*Check:* the same config with `head = "classifier"` trains and reports top-1 on `val`.

**FR-408.** THE SYSTEM SHALL resolve set, name, rarity, category, types, regulation mark and
legality of an identified card from the catalog, and MAY train auxiliary heads that predict
set, rarity and category directly, enabled by config, for photos whose card is not in the
index.
*Check:* an identification result lists all card labels of the matched card. With auxiliary
heads on, the run reports their accuracy.

**FR-409.** WHEN `augment.online` is true, THE SYSTEM SHALL apply light seeded augmentation
(color jitter, small blur, random crop) to training images in the loader, and SHALL record the
settings in the run.
*Check:* two epochs over one image give two different tensors, and the same seed reproduces
both.

**FR-410.** THE SYSTEM SHALL seed Python, NumPy, PyTorch and the loader workers from the run
seed, and SHALL record the seed, library versions and code version in the run metadata.
*Check:* two CPU runs with one seed give equal metrics. `model-card.json` holds the seed and
versions.

**FR-411.** THE SYSTEM SHALL write, under `runs/<name>/`, a copy of the config,
`metrics.jsonl`, the best and the last checkpoint by validation metric, and
`model-card.json`, and SHALL resume from the last checkpoint with `--resume`.
*Check:* a run stopped after epoch 1 and resumed ends with the metrics of an uninterrupted run
on CPU.

**FR-412.** THE SYSTEM SHALL choose CUDA when available, then MPS on Apple silicon, then CPU,
unless the config names a device.
*Check:* a test with a faked availability check picks each in turn.

**FR-413.** THE SYSTEM SHALL read training data only from the build's manifest, and SHALL NOT
discover images by listing directories.
*Check:* an extra image dropped into the build directory does not appear in any epoch.

**FR-414.** THE SYSTEM SHALL provide a dataset class that reads the manifest and yields, for
each variant, the image tensor, the card index and the card label record.
*Check:* the class yields exactly the manifest's files for a split, in a seeded order.

## Current state and gaps

What exists: nothing in the package. `notebooks/gen_model.ipynb` trains a small CNN with
`Adam(lr=0.000001)` for 500 epochs and `xfer_model.ipynb` fine-tunes MobileNetV2 with a
hard-coded `num_classes = 116`. Both hard-code `/home/...` paths. `scripts/run_mkimgclsfr.sh`
calls `make_image_classifier`, which tensorflow-hub removed in 0.14.0 (2023-07-13). The model
container installs tensorflow-hub 0.16.1, which needs `tf-keras>=2.14.1`, on a TensorFlow 2.13
base image (#78).

| Requirement | Closed by |
|---|---|
| FR-401, FR-409, FR-413, FR-414 | #101 |
| FR-402, FR-403 | #100 |
| FR-404, FR-410, FR-411, FR-412 | #102 |
| FR-405, FR-406 | #103 |
| FR-407 | #104 |
| FR-408 | #105 |
