# Requirements traceability matrix

One row per requirement. `Implementation ref` and `Test ref` stay `-` until code and a tagged
test exist. Tests carry the tag `ReqID: <id>` in their docstring. `Issue` is the issue that
closes the gap. Status words are in [README.md](README.md).

| ReqID | Requirement | Type | Implementation ref | Test ref (tag) | Status | Issue |
|---|---|---|---|---|---|---|
| FR-101 | THE SYSTEM SHALL read cards and sets from a source only through a `CardSource` adapter, so that no module outside the adapter imports a source SDK or makes a source request. | FR | - | - | Planned | #85 |
| FR-102 | WHEN a source record omits an optional field, THE SYSTEM SHALL store the card with that field null and SHALL NOT fail the fetch. | FR | - | - | Planned | #85 |
| FR-103 | IF one record fails to parse, THEN THE SYSTEM SHALL log the source id and the reason, continue with the remaining records, print the failure count at the end, and exit non-zero. | FR | - | - | Planned | #85 |
| FR-104 | THE SYSTEM SHALL use the TCGdex card id as the canonical card id and the TCGdex set id as the canonical set id. | FR | - | - | Planned | #77 |
| FR-105 | THE SYSTEM SHALL keep every earlier id of a card in `legacy_ids` and SHALL provide a lookup from any legacy id to the canonical id. | FR | - | - | Planned | #86 |
| FR-106 | THE SYSTEM SHALL store a card label record, as defined above, for every card the source lists. | FR | - | - | Planned | #88 |
| FR-107 | THE SYSTEM SHALL persist the catalog as plain files with `schema_version`, readable without this package, and SHALL NOT persist it with pickle. | FR | - | - | Planned | #88 |
| FR-108 | THE SYSTEM SHALL store a set record for every set the source lists. | FR | - | - | Planned | #88 |
| FR-109 | WHEN a request fails with a network error, a timeout, HTTP 429 or HTTP 5xx, THE SYSTEM SHALL retry with exponential backoff up to a configured limit, then record the failure and continue. | FR | - | - | Planned | #85 |
| FR-110 | WHEN an image is downloaded, THE SYSTEM SHALL decode it with Pillow, check that both sides are at least a configured minimum, and reject it otherwise without writing it to the image store. | FR | - | - | Planned | #82 |
| FR-111 | THE SYSTEM SHALL write catalog files and images to a temporary name in the same directory and rename them into place, so a crash leaves either the old file or the new one. | FR | - | - | Planned | #82 |
| FR-112 | THE SYSTEM SHALL keep one image index, `images.jsonl`, with the file name, SHA-256, width, height, source URL and fetch time of every reference scan, and SHALL rebuild it from the image directory on request. | FR | - | - | Planned | #88 |
| FR-113 | THE SYSTEM SHALL NOT perform network or disk-creating work when a manager object is constructed. | FR | - | - | Planned | #91 |
| FR-114 | WHEN `card-data --refresh` runs on an empty data root, THE SYSTEM SHALL fetch each resource once. | FR | - | - | Planned | #91 |
| FR-115 | THE SYSTEM SHALL find games and their adapters through a registry, SHALL derive the `--card-type` choices from it, and SHALL keep game-specific imports out of the core modules. | FR | - | - | Planned | #92 |
| FR-116 | WHEN an image is stored, THE SYSTEM SHALL record its source URL in the image index, and THE SYSTEM SHALL keep `data/` out of git and out of container images. | FR | - | - | Planned | #98 |
| FR-201 | WHEN the generator saves an image, THE SYSTEM SHALL write a sidecar that parses with the standard `json` module, and SHALL write the sidecar and the image so that neither exists without the other after a crash. | FR | - | - | Planned | #75 |
| FR-202 | THE SYSTEM SHALL record the transform steps in an ordered `steps` list, with each step's name and parameters, and SHALL NOT merge steps into one flat object. | FR | - | - | Planned | #95 |
| FR-203 | THE SYSTEM SHALL write only JSON-native values to a sidecar, converting NumPy scalars and arrays before writing. | FR | - | - | Planned | #75 |
| FR-204 | THE SYSTEM SHALL derive each image's random seed from the build seed, the card id and the image index, and SHALL produce byte-identical images for equal inputs regardless of the number of worker processes. | FR | - | - | Planned | #79 |
| FR-205 | THE SYSTEM SHALL draw all randomness in transforms, backgrounds and placement from the per-image seeded generator, and SHALL NOT use the global `random` module or an unseeded library generator. | FR | - | - | Planned | #79 |
| FR-206 | THE SYSTEM SHALL read transform probabilities and ranges from a TOML generator config, SHALL ship a default config that reproduces the documented defaults, and SHALL record the config in the build manifest. | FR | - | - | Planned | #94 |
| FR-207 | WHEN the config enables color or noise transforms, THE SYSTEM SHALL apply them with the configured probability. | FR | - | - | Planned | #94 |
| FR-208 | THE SYSTEM SHALL size the working canvas to contain the whole transformed card, and SHALL crop the card at the frame edge only as far as the configured `max_offframe_fraction` allows. | FR | - | - | Planned | #96 |
| FR-209 | THE SYSTEM SHALL scale every reference scan to a configured reference height before other transforms, so output card size does not depend on the source scan's resolution. | FR | - | - | Planned | #96 |
| FR-210 | THE SYSTEM SHALL ignore files in the backgrounds directory that Pillow cannot open, SHALL crop backgrounds to the output aspect ratio instead of stretching them, and SHALL fail before any worker starts when a build needs backgrounds and finds none. | FR | - | - | Planned | #80 |
| FR-211 | IF generation for one card fails, THEN THE SYSTEM SHALL record the card id and the error, continue with the other cards, print generated, skipped and failed counts, and exit 1 when any card failed. | FR | - | - | Planned | #80 |
| FR-212 | THE SYSTEM SHALL count a variant toward a card's quota only when its image and sidecar both exist and the sidecar parses, and SHALL report orphans. | FR | - | - | Planned | #75 |
| FR-213 | THE SYSTEM SHALL produce images at a configured square size and format, defaulting to 224 pixels and PNG. | FR | - | - | Planned | #94 |
| FR-214 | THE SYSTEM SHALL provide optional realism transforms for glare, blur, lighting gradient, JPEG compression, sleeve reflection and partial occlusion, each controlled by the config and each recorded as a step. | FR | - | - | Planned | #109 |
| FR-215 | WHEN `trim-dataset` removes images, THE SYSTEM SHALL remove each image's sidecar with it, SHALL choose images to keep deterministically from the seed after sorting by name, and SHALL update any dataset map or manifest that lists them. | FR | - | - | Planned | #97 |
| FR-301 | THE SYSTEM SHALL accept a selection file with the keys above and SHALL reject an unknown key with an error that names it. | FR | - | - | Planned | #89 |
| FR-302 | THE SYSTEM SHALL decide format legality per card from the card's `legal_standard` and `legal_expanded` flags, and SHALL NOT infer a card's legality from its set. | FR | - | - | Planned | #87 |
| FR-303 | WHEN a selected format needs a legality flag that is null for some cards, THE SYSTEM SHALL leave those cards out, print how many it left out, and fail instead when `--strict` is set. | FR | - | - | Planned | #87 |
| FR-304 | THE SYSTEM SHALL provide `select --dry-run`, which resolves a selection against the catalog and prints the card count, the count per set and the total variants for a given `images_per_card`, and writes nothing. | FR | - | - | Planned | #89 |
| FR-305 | THE SYSTEM SHALL provide `build`, which takes a selection, a generator config, a seed and `images_per_card`, generates the missing variants, and writes a manifest. | FR | - | - | Planned | #90 |
| FR-306 | THE SYSTEM SHALL record in the manifest every field listed above. | FR | - | - | Planned | #90 |
| FR-307 | THE SYSTEM SHALL store each variant once and let builds reference it, so builds that share a card and a seed share its files. | FR | - | - | Planned | #90 |
| FR-308 | THE SYSTEM SHALL assign each variant to `train`, `val` or `test` in the manifest, using one of two strategies: `per_card`, which splits each card's variants by fraction, and `by_set`, which holds out whole sets for `val` and `test`. The default is `per_card` at 0.8, 0.1, 0.1. | FR | - | - | Planned | #90 |
| FR-309 | THE SYSTEM SHALL assign splits from a hash of the seed and the variant's identity, so adding cards or variants never moves an existing variant to a different split. | FR | - | - | Planned | #90 |
| FR-310 | THE SYSTEM SHALL provide `export --layout imagefolder`, which writes a class-per-directory tree of symlinks to a path outside the build's image directory, for tools that expect that layout. | FR | - | - | Planned | #81 |
| FR-311 | THE SYSTEM SHALL write a statistics report for a build, as JSON and Markdown, with cards and variants per set, per rarity and per category, variants per card (minimum, median, maximum), the use count of every transform step, the background mix, and failures. | FR | - | - | Planned | #93 |
| FR-312 | THE SYSTEM SHALL count a variant once when it scans a build, whatever links or exports point at it. | FR | - | - | Planned | #81 |
| FR-313 | THE SYSTEM SHALL describe card id filters as exact ids or a shell-style glob (`id_glob`), and SHALL remove the `--str-filter` option that claims to match a substring while matching a prefix. | FR | - | - | Planned | #89 |
| FR-401 | THE SYSTEM SHALL provide `train`, which takes a run config, and SHALL stop before training when the manifest is missing or a sampled file's SHA-256 differs from the manifest. | FR | - | - | Planned | #101 |
| FR-402 | THE SYSTEM SHALL keep a backbone registry in which each entry holds the registry name, the timm model name, the pretrained weight tag, the input size, the normalization mean and standard deviation, the weight source and the weight licence, and adding a backbone SHALL need only a new entry. | FR | - | - | Planned | #100 |
| FR-403 | WHEN a backbone's weight licence is unknown or forbids commercial use, THE SYSTEM SHALL stop and ask for `--accept-licence`, and SHALL record the accepted licence in the run metadata. | FR | - | - | Planned | #100 |
| FR-404 | WHEN the head is `embedding`, THE SYSTEM SHALL train an embedding on the `train` split with a metric-learning loss chosen in the config, SHALL support a schedule that freezes the backbone for the first epochs, and SHALL compute a validation metric each epoch. | FR | - | - | Planned | #102 |
| FR-405 | THE SYSTEM SHALL build a reference index by embedding one reference scan per card in the build, store the vectors and ids in plain files, record the model hash in the index, and answer a query with the top-k card ids by cosine similarity. | FR | - | - | Planned | #103 |
| FR-406 | WHEN cards are added to the catalog, THE SYSTEM SHALL add their vectors to an existing index with `index add`, and SHALL NOT retrain. | FR | - | - | Planned | #103 |
| FR-407 | WHEN the head is `classifier`, THE SYSTEM SHALL train a softmax over the build's card ids with the same loader, backbone registry, seed handling and run layout, and SHALL write a label map. | FR | - | - | Planned | #104 |
| FR-408 | THE SYSTEM SHALL resolve set, name, rarity, category, types, regulation mark and legality of an identified card from the catalog, and MAY train auxiliary heads that predict set, rarity and category directly, enabled by config, for photos whose card is not in the index. | FR | - | - | Planned | #105 |
| FR-409 | WHEN `augment.online` is true, THE SYSTEM SHALL apply light seeded augmentation (color jitter, small blur, random crop) to training images in the loader, and SHALL record the settings in the run. | FR | - | - | Planned | #101 |
| FR-410 | THE SYSTEM SHALL seed Python, NumPy, PyTorch and the loader workers from the run seed, and SHALL record the seed, library versions and code version in the run metadata. | FR | - | - | Planned | #102 |
| FR-411 | THE SYSTEM SHALL write, under `runs/<name>/`, a copy of the config, `metrics.jsonl`, the best and the last checkpoint by validation metric, and `model-card.json`, and SHALL resume from the last checkpoint with `--resume`. | FR | - | - | Planned | #102 |
| FR-412 | THE SYSTEM SHALL choose CUDA when available, then MPS on Apple silicon, then CPU, unless the config names a device. | FR | - | - | Planned | #102 |
| FR-413 | THE SYSTEM SHALL read training data only from the build's manifest, and SHALL NOT discover images by listing directories. | FR | - | - | Planned | #101 |
| FR-414 | THE SYSTEM SHALL provide a dataset class that reads the manifest and yields, for each variant, the image tensor, the card index and the card label record. | FR | - | - | Planned | #101 |
| FR-501 | THE SYSTEM SHALL read a real-photo set from `labels.csv` and a photos directory, SHALL reject a row whose photo is missing or whose `card_id` is not in the catalog, and SHALL report the SHA-256 of the labels file. | FR | - | - | Planned | #106 |
| FR-502 | THE SYSTEM SHALL provide `evaluate`, which runs a model and index on a photo set and reports top-1 and top-5 accuracy for card id, and accuracy for set, name, rarity, category and regulation mark taken from the matched card's catalog record. | FR | - | - | Planned | #106 |
| FR-503 | THE SYSTEM SHALL write a report as JSON and Markdown with the metrics, a per-set breakdown, a breakdown per tag column, the most confused card pairs, the list of failed photos, and the hashes of the model, the index, the manifest and the photo labels. | FR | - | - | Planned | #106 |
| FR-504 | THE SYSTEM SHALL provide `compare`, which tabulates several reports side by side and SHALL refuse reports that used different photo-label hashes. | FR | - | - | Planned | #107 |
| FR-505 | THE SYSTEM SHALL label every metric computed on synthetic validation images as synthetic and SHALL NOT place it in the headline table. | FR | - | - | Planned | #106 |
| FR-506 | WHEN a photo's best match scores below a threshold, THE SYSTEM SHALL return "unknown", SHALL report the unknown rate for in-index and out-of-index photos, and SHALL report how the threshold was chosen. | FR | - | - | Planned | #106 |
| FR-507 | THE SYSTEM SHALL report model size on disk and median per-image latency on the device used. | FR | - | - | Planned | #106 |
| FR-601 | THE SYSTEM SHALL provide `identify`, which takes one or more photo paths, a run or bundle, and `--top-k`, and prints one result object per photo as JSON lines. | FR | - | - | Planned | #108 |
| FR-602 | THE SYSTEM SHALL use one preprocessing function, taking its parameters from the backbone registry entry, for training, indexing, evaluation and inference. | FR | - | - | Planned | #100 |
| FR-603 | THE SYSTEM SHALL export the embedding model to ONNX with the preprocessing parameters stored in the file's metadata, and SHALL verify that ONNX and PyTorch outputs for sample images differ by less than a stated tolerance. | FR | - | - | Planned | #108 |
| FR-604 | THE SYSTEM SHALL write a self-contained bundle directory with `model.onnx`, the index vectors, the index ids, the card label records of indexed cards, and `model-card.json`, and `identify` SHALL run from the bundle alone. | FR | - | - | Planned | #108 |
| FR-605 | WHEN `identify` reads a photo, THE SYSTEM SHALL apply EXIF orientation, convert to RGB, and report a clear error for a file that is not an image, without stopping on the other photos. | FR | - | - | Planned | #108 |
| NFR-1 | THE SYSTEM SHALL support Python 3.13 and 3.14, and CI SHALL run the test suite on both. | NFR | `.github/workflows/ci.yml:22` | `.github/workflows/ci.yml` | Done | - |
| NFR-2 | THE SYSTEM SHALL record the code version, the config hash, the seed and the hashes of input files in every catalog, build, run, index, bundle and report it writes. | NFR | - | - | Planned | #90 |
| NFR-3 | THE SYSTEM SHALL NOT persist data with pickle, and SHALL NOT load a pickle file that a user supplies. | NFR | - | - | Planned | #88 |
| NFR-4 | THE SYSTEM SHALL set a timeout and a bounded retry count on every outbound HTTP request. | NFR | - | - | Planned | #82 |
| NFR-5 | THE SYSTEM SHALL test the transform chain, the serializers and the file layout without stubbing them. A test MAY fake the network, the process pool and the clock. | NFR | - | - | Planned | #84 |
| NFR-6 | WHEN a build or training command finishes, THE SYSTEM SHALL print its duration and its throughput (images per second). | NFR | - | - | Planned | #90 |
| NFR-7 | THE SYSTEM SHALL validate downloaded images before use, SHALL set a maximum pixel count for decoding, and SHALL build file names only from ids that match `^[a-z0-9][a-z0-9._-]*$`. | NFR | - | - | Planned | #82 |
| NFR-8 | THE SYSTEM SHALL record the licence of every pretrained weight it uses, SHALL keep card images out of git and out of container images, and SHALL document where backgrounds come from. | NFR | - | - | Planned | #98 |
| NFR-9 | THE SYSTEM SHALL let a new game be added by a games package and one registry entry, with no edit to core modules. | NFR | - | - | Planned | #92 |
| NFR-10 | THE SYSTEM SHALL run every command without a graphical display. | NFR | `card_identifier/cli/` | `.github/workflows/ci.yml` | Done | - |
| NFR-11 | THE SYSTEM SHALL list every requirement in `docs/rtm.md`, and a script SHALL fail when a requirement is missing from it or a test tag names an unknown requirement. | NFR | - | - | Planned | #99 |
| NFR-12 | THE SYSTEM SHALL pass its debug setting to worker processes, because `spawn` workers do not inherit logging configuration. | NFR | `card_identifier/dataset/generator.py:149` | - | Done | #84 |
