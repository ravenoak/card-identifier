# Critical examination, 2026-10-09

Scope: the whole repository at commit `eaea9c3` (`main`), its documentation, its tests, its
CI and container files, and the external services it depends on. Method and limits are at
the end. Every finding below is a record in the schema of the filing contract: claim,
falsifier, evidence, verdict, severity, routing. Issue numbers in the last column are
filled in when the issues are filed.

## Summary

- 32 findings were examined. A second model checked 30 of them: 27 CONFIRMED, 3 ESCALATE
  (resolved below), none cleared. It found the other 2 defects, which were added. One finding
  was held, so 31 findings were filed.
- Two of the 31 (`cat-api-sunset`, `trn-trainer`) were too broad to act on. They became 3 and
  5 issues, so the backlog holds 37 issues. The owner chose to file all of them, above the
  filing contract's cap of 12 per run.
- One finding was routed `hold` and not filed (`infra-local-ci`).
- Two defects came from the verifier and were added: `gen-meta-overwrite` and
  `gen-perspective-clip`.

What works and was checked clean on 2026-10-09:

- `uv run pytest -n auto`: 42 passed, 1 skipped (TensorFlow not installed).
- `ruff check .`: all checks passed. `ruff format --check .`: 66 files already formatted.
  `pyright`: 0 errors, 0 warnings.
- GitHub Actions on `main` (last 3 runs, `gh run list`): success.
- CI pins actions by commit SHA, uses `persist-credentials: false` and read-only permissions.
- Dependabot covers `uv` and `github-actions` with a 7-day cooldown.

The suite passes because it avoids the failing code. See `gen-json-crash`.

## Findings

### gen-json-crash

- **title:** Fix create-dataset failing on every image (sidecar JSON write)
- **domain:** generation
- **artifact:** `card_identifier/image/transformers.py:116`
- **claim:** create-dataset fails on every image: the perspective step stores a NumPy array that json.dump cannot write, after the PNG is saved.
- **falsifier:** A run of `gen_random_dataset` with the real transform chain and a valid background completes and leaves parseable sidecars.
- **evidence:**
  - `card_identifier/image/transformers.py:116` puts `coefficients` (a NumPy array from `np.linalg.lstsq`) in the meta dict.
  - `card_identifier/dataset/generator.py:77-84` saves the PNG, then calls `json.dump` on the meta.
  - `card_identifier/dataset/generator.py:130-132` counts `*.png` files only.
  - Verifier repro (a 734x1024 RGBA PNG and one JPEG background, seeds 0 to 4): 5 of 5 runs raise the `TypeError`, each leaving a PNG and a truncated `.json`.
  - `tests/test_dataset_builder.py:41-45` and `tests/test_dataset_generator.py:49-53,84-88` replace `random_perspective_transform`.
- **verdict:** CONFIRMED
- **severity:** Critical
- **priority:** P0. No image can be generated until this is fixed.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-201, FR-203, FR-212
- **issue:** #75

### cat-card-parse

- **title:** Fix card-data failing to parse any card from the Pokemon TCG API
- **domain:** catalog
- **artifact:** `card_identifier/cards/pokemon/api_client.py:48`
- **claim:** card-data cannot fetch any card, because the SDK requires fields (legalities, set.printedTotal) that current cards lack.
- **falsifier:** `PokemonTCGSDKClient().iter_cards()` returns `me55c` cards when fed the current API payload.
- **evidence:**
  - `card_identifier/cards/pokemon/api_client.py:48` calls `Card.all()`.
  - pokemontcgsdk 3.4.0: `card.py` declares `legalities: Legality` with no default; `set.py` declares `printedTotal: int`; `querybuilder.py:63` parses a page in one list comprehension.
  - Repro by a reviewer: `RestClient.get` patched to return an `me55c` card without `legalities` raises `MissingValueError: missing value for field "legalities"`; with `legalities` but a set without `printedTotal` it raises on `set.printedTotal`.
  - `PokemonTCG/pokemon-tcg-data` `cards/en/me55c.json` has `"legalities": null` and no `set` key on its cards.
- **verdict:** CONFIRMED
- **severity:** Critical
- **priority:** P0. Blocks every catalog refresh until the TCGdex adapter lands.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** none
- **issue:** #76

### cat-sunset-spike

- **title:** Spike: map TCGdex ids to current ids and check TCGdex coverage
- **domain:** catalog
- **artifact:** `Set id comparison, 2026-10-09: `gh api repos/PokemonTCG/poke`
- **claim:** Legacy and TCGdex ids differ (50 of 176 set ids have no same-named TCGdex set), and no mapping or coverage report exists.
- **falsifier:** Every legacy set and card id maps to one TCGdex id by set id and number alone.
- **evidence:**
  - Set id comparison, 2026-10-09: `gh api repos/PokemonTCG/pokemon-tcg-data/contents/sets/en.json` against `https://api.tcgdex.net/v2/en/sets` (176 vs 220 sets, 126 shared).
  - `curl https://api.tcgdex.net/v2/en/sets/30th-c` returns 30 cards, release date 2026-09-16, `legal.standard: false`. `tests/conftest.py:12` has `me55c` as `standard: Legal`.
  - Set totals: 20,530 in `pokemon-tcg-data`; 21,484 in the 205 physical TCGdex sets (23,964 with the 15 TCG Pocket sets of series `tcgp`).
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P0. Gates the adapter and the id migration, and the API sunset is dated.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **ledger row:** split from `cat-api-sunset`
- **requirements:** none
- **issue:** #77

### trn-tfhub-removed

- **title:** Retire the TensorFlow Hub training path and container
- **domain:** training
- **artifact:** `scripts/run_mkimgclsfr.sh:35`
- **claim:** The training script and container depend on make_image_classifier, which tensorflow-hub removed in 0.14.0.
- **falsifier:** `pip install tensorflow-hub` in the model image provides a working `make_image_classifier` command.
- **evidence:**
  - `scripts/run_mkimgclsfr.sh:35` runs `make_image_classifier`.
  - `deploy/model_generator/Dockerfile:4,14` uses `tensorflow/tensorflow:2.13.0-gpu-jupyter` and `pip install --upgrade "tensorflow-hub[make_image_classifier]"`.
  - tensorflow/hub release v0.14.0 (2023-07-13): "Remove make_image_classifier and make_nearest_neighbour_index". PyPI tensorflow-hub 0.16.1 requires `tf-keras>=2.14.1`.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. A broken path with documentation is worse than none; cheap to remove.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** none
- **issue:** #78

### gen-repro

- **title:** Make dataset generation reproducible across workers
- **domain:** generation
- **artifact:** `card_identifier/dataset/generator.py:104`
- **claim:** Reproducibility is claimed and false: spawned workers ignore the saved random state, noise has its own generator, and trimming depends on filesystem order.
- **falsifier:** Two builds with the same seed and different worker counts produce identical image hashes today.
- **evidence:**
  - `card_identifier/dataset/generator.py:104` loads state; `:150-151` starts a `spawn` pool.
  - Reviewer repro: `random.seed(42)` in the parent, then `Pool(2).starmap(random_rotate)` under `spawn`: run 1 gave `[194, 269, 333, 110]`, run 2 `[257, 74, 355, 66]`.
  - `card_identifier/image/transformers.py:25` calls `skimage.util.random_noise` with no `rng`; scikit-image 0.26.0 uses `rng=None`.
  - `card_identifier/cli/trim_dataset.py:51-53` shuffles `image_dir.glob(...)` output; `card_identifier/cli/random_state.py:37` names the wrong file.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. Reproducibility is a stated goal and silently false.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-204, FR-205, NFR-3
- **issue:** #79

### gen-failure-isolation

- **title:** Isolate failures in dataset generation and report a summary
- **domain:** generation
- **artifact:** `card_identifier/image/background.py:33`
- **claim:** A non-image file in the backgrounds directory stops a worker chunk and the command exits 1 with a traceback and no summary; other failures exit 0.
- **falsifier:** A directory containing a `.DS_Store` file and one JPEG generates images without error.
- **evidence:**
  - `card_identifier/image/background.py:33` lists every file in the directory; `:40` opens the chosen one with Pillow; `:43` resizes without keeping the aspect ratio.
  - Reviewer repro: a backgrounds directory holding a non-image file raised `UnidentifiedImageError` for seeds 0 and 4 of 6.
  - `card_identifier/dataset/generator.py:153` uses `pool.starmap`; CPython `Pool.starmap` raises the first worker error after the other chunks finish.
  - `card_identifier/dataset/generator.py:39,121` and `util.py:41` log and continue with exit 0.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. One bad file costs a long run and hides the cause.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-210, FR-211
- **issue:** #80

### sel-symlinks-dir

- **title:** Fix mk_symlinks treating its own output directory as a set
- **domain:** selection
- **artifact:** `card_identifier/dataset/__init__.py:97`
- **claim:** mk_symlinks treats its own output directory as a set, and scan_dataset_dir counts linked images twice.
- **falsifier:** After one run of `mk_symlinks('all')`, `symlinks/all/` holds only card directories and `scan_dataset_dir()` has no key `all`.
- **evidence:**
  - `card_identifier/dataset/__init__.py:97` creates `symlinks/<mode>` before `:99` globs the dataset directory.
  - `card_identifier/dataset/__init__.py:60-65` takes `rel_parts[1]` of `symlinks/all/<card>/x.png`, which is `all`.
  - Code reading, then a second reviewer ran it on a temporary tree and saw `symlinks/all/all` on the first run.
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P1. Corrupts class lists for any run after the first.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-312
- **issue:** #81

### cat-resilience

- **title:** Make downloads and catalog writes resilient
- **domain:** catalog
- **artifact:** `restclient.py`
- **claim:** Downloads and writes lack timeouts, retries for 5xx, image validation and atomic writes.
- **falsifier:** A 200 response with an HTML body is rejected and not stored today.
- **evidence:**
  - pokemontcgsdk `restclient.py`: `urlopen(req)` with no `timeout`.
  - `card_identifier/util.py:24` sets `status_forcelist=[429]`; `:34-40` writes any `image.ok` body.
  - `card_identifier/cards/pokemon/__init__.py:82-85` skips an existing file unless `force`.
  - `card_identifier/storage.py:12` and `util.py:37` open the target path directly.
  - `curl -s -w '%{http_code}' https://api.pokemontcg.io/v2/cards?pageSize=1` returned `500` at 2026-10-10 06:00 UTC and `200` at 06:39.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. Silent corrupt downloads poison a dataset with no signal.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-109, FR-110, FR-111, NFR-4, NFR-7
- **issue:** #82

### docs-training-drift

- **title:** Correct or remove docs/model_training.md
- **domain:** docs
- **artifact:** `docs/model_training.md:57-60`
- **claim:** docs/model_training.md names build arguments, a Python version and an example id that do not exist.
- **falsifier:** Every build argument and example in `docs/model_training.md` works as written.
- **evidence:**
  - `docs/model_training.md:57-60` lists `PACKAGE_NAME`, `PACKAGE_VER` and `PYTHON_VERSION` default 3.10; `deploy/dataset_generator/Dockerfile` has none of the first two and defaults Python to 3.14.
  - `docs/model_training.md:12` uses `base_set`; the Base Set id is `base1`.
  - `scripts/run_mkimgclsfr.sh:32-33` builds file names from the namespace argument, so a `/` in it breaks the label and TFLite paths.
- **verdict:** CONFIRMED
- **severity:** Low
- **priority:** P2. Misleading docs; small.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** none
- **issue:** #83

### test-mocked-core

- **title:** Test the real transform chain and stop mutating global config
- **domain:** tests
- **artifact:** `tests/test_dataset_builder.py:41-45`
- **claim:** Tests stub the failing transform, mutate global config, and no coverage is measured.
- **falsifier:** Removing the stubs leaves the suite green today.
- **evidence:**
  - `tests/test_dataset_builder.py:41-45` and `tests/test_dataset_generator.py:49-53,84-88` replace `random_perspective_transform`.
  - `tests/test_cli.py:29-31` and `tests/test_dataset_generator.py:38-40` assign to `config` attributes directly.
  - `rg coverage pyproject.toml uv.lock` finds no match; `grep -rn CARDIDENT_DEBUG tests` finds nothing.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. Tests that stub the failure site cannot catch it.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** NFR-5, NFR-12
- **issue:** #84

### cat-sunset-adapter

- **title:** Add a TCGdex source adapter behind a CardSource interface
- **domain:** catalog
- **artifact:** `pokemon-tcg-data README (commit 2026-09-17): "scheduled to b`
- **claim:** The catalog depends on a source that goes offline on 2027-03-01 and an SDK with no release since 2021-12-21.
- **falsifier:** The pokemontcg.io API stays available and the SDK parses current cards after 2027-03-01.
- **evidence:**
  - pokemon-tcg-data README (commit 2026-09-17): "scheduled to be taken offline on March 1, 2027".
  - PyPI `pokemontcgsdk` 3.4.0, uploaded 2021-12-21.
  - TCGdex card record fields seen 2026-10-09: `id`, `localId`, `name`, `category`, `rarity`, `hp`, `types`, `illustrator`, `regulationMark`, `legal.standard`, `legal.expanded`, `image`, `set`, `updated`.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P0. Without it the pipeline has no card source after 2027-03-01.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **ledger row:** split from `cat-api-sunset`
- **requirements:** FR-101, FR-102, FR-103, FR-104, FR-117
- **issue:** #85

### cat-sunset-migrate

- **title:** Migrate existing dataset directories to canonical card ids
- **domain:** catalog
- **artifact:** `card_identifier/dataset/generator.py:124-125`
- **claim:** Existing datasets and maps use legacy ids, some of which change under the new source.
- **falsifier:** Every directory under an existing dataset resolves through `legacy_ids` to a canonical id without renaming.
- **evidence:**
  - `card_identifier/dataset/generator.py:124-125` derives `<set>/<card-id>` from the old id.
  - Set id mismatches: see the crosswalk spike (50 of 176 legacy set ids have no same-named TCGdex set).
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P1. Protects existing generated data; no new capability.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **ledger row:** split from `cat-api-sunset`
- **requirements:** FR-105, NFR-3
- **issue:** #86

### sel-legal-semantics

- **title:** Decide format legality per card, not per set
- **domain:** selection
- **artifact:** `card_identifier/cards/pokemon/__init__.py:31-36`
- **claim:** legal mode unions Standard and Expanded at set level, so it selects almost everything and never means Standard.
- **falsifier:** A fixture set holding one rotated and one legal card is split correctly by `legal` mode today.
- **evidence:**
  - `card_identifier/cards/pokemon/__init__.py:31-36` unions the two queries.
  - pokeguardian.com rotation notice (2026-01-09): G-mark cards leave Standard on 2026-04-10; H, I and J remain.
  - TCGdex card record `swsh3-136` carries `regulationMark: D` and `legal: {standard: false, expanded: true}` (fetched 2026-10-09).
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. 'Tournament legal' is a stated requirement and today's answer is wrong.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-302, FR-303
- **issue:** #87

### cat-label-catalog

- **title:** Add a label catalog with a versioned schema, replacing pickles
- **domain:** catalog
- **artifact:** `card_identifier/cards/pokemon/__init__.py:93-95`
- **claim:** Card metadata is a pickle of SDK objects with two same-named maps, and no record of the labels the identifier should report.
- **falsifier:** Catalog data is readable without importing `card_identifier` or `pokemontcgsdk` today.
- **evidence:**
  - `card_identifier/cards/pokemon/__init__.py:93-95` pickles `cards.pickle`, `sets.pickle` and `cards_by_set.pickle`.
  - `card_identifier/dataset/generator.py:107` reads `barrel/<game>/card_image_map.pickle`; `card_identifier/dataset/__init__.py:29,46` reads another file with the same name.
  - `card_identifier/dataset/generator.py:124` uses `card_id.split("-")[0]` as the set id.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P0. The TCGdex adapter (P0) writes into it, and every later stage reads it.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-106, FR-107, FR-108, FR-112, NFR-3
- **issue:** #88

### sel-selection

- **title:** Add declarative selection and a select --dry-run command
- **domain:** selection
- **artifact:** `card_identifier/dataset/__init__.py:72-97`
- **claim:** Subset selection is three hard-coded modes in a library call, with a filter option whose help text is wrong.
- **falsifier:** A CLI command today selects cards by rarity or regulation mark.
- **evidence:**
  - `card_identifier/dataset/__init__.py:72-97` implements `all`, `legal` and `sets` only; no CLI calls `mk_symlinks`.
  - `card_identifier/cli/create_dataset.py:23,63` says 'substring'; `card_identifier/dataset/generator.py:123` calls `startswith`.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. Core user requirement; nothing else in selection works without it.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-301, FR-304, FR-313
- **issue:** #89

### sel-manifest-splits

- **title:** Add dataset builds with a manifest and train/val/test splits
- **domain:** selection
- **artifact:** `card_identifier/dataset/generator.py:90-153`
- **claim:** A dataset has no manifest of how it was made and no train/validation/test split.
- **falsifier:** A command today records the seed, config and card list of a dataset.
- **evidence:**
  - `card_identifier/dataset/generator.py:90-153` builds work lists and writes files; nothing writes a manifest.
  - `rg -i 'manifest|split|validation' card_identifier` finds only `str.split`.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. Training and evaluation both depend on it.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-305, FR-306, FR-307, FR-308, FR-309, FR-310, NFR-2, NFR-6
- **issue:** #90

### cat-ctor-io

- **title:** Stop managers from doing network work in constructors
- **domain:** catalog
- **artifact:** `card_identifier/cards/pokemon/__init__.py:96-98`
- **claim:** CardManager's constructor does network work, and a cold refresh fetches everything twice.
- **falsifier:** Constructing `CardManager()` on an empty data root makes no request today.
- **evidence:**
  - `card_identifier/cards/pokemon/__init__.py:96-98` calls `get_data` for cards, sets and the set map in `__init__`.
  - `card_identifier/cli/card_data.py:48-51` constructs the manager, then calls `refresh_data()`.
- **verdict:** CONFIRMED
- **severity:** Low
- **priority:** P3. Cleanup that makes testing easier.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-113, FR-114
- **issue:** #91

### cat-game-registry

- **title:** Replace the hard-coded game list and dispatch with a registry
- **domain:** catalog
- **artifact:** `card_identifier/data.py:6`
- **claim:** Adding a game needs edits in four places, and the game-agnostic dataset module imports Pokemon code.
- **falsifier:** A stub game can be added by one registry entry today.
- **evidence:**
  - `card_identifier/data.py:6`, `card_identifier/cli/card_data.py:46`, `card_identifier/dataset/__init__.py:7`, `scripts/run_mkimgclsfr.sh:20-28`.
- **verdict:** CONFIRMED
- **severity:** Low
- **priority:** P3. Only matters when a second game starts.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-115, NFR-9
- **issue:** #92

### sel-stats-report

- **title:** Add a dataset statistics report
- **domain:** selection
- **artifact:** `DESIGN.md:38-39`
- **claim:** Nothing reports what a build holds (DESIGN.md listed this as a wanted feature).
- **falsifier:** A command today reports variants per set or transform usage.
- **evidence:**
  - `DESIGN.md:38-39` (removed from the tree by the docs change that adds this backlog; see git history).
- **verdict:** CONFIRMED
- **severity:** Low
- **priority:** P3. Useful, not blocking.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-311
- **issue:** #93

### gen-config

- **title:** Move transform parameters into a generator config
- **domain:** generation
- **artifact:** `card_identifier/dataset/generator.py:25-30,138`
- **claim:** Transform ranges are constants, and the color and noise branch can never run.
- **falsifier:** Any code path passes `xform=True` today.
- **evidence:**
  - `card_identifier/dataset/generator.py:25-30,138` (work tuple has three items; `xform=False` default).
  - `rg xform card_identifier scripts` finds only the signature default (reviewer check).
  - `card_identifier/image/transformers.py:43,64` hard-code `0.3` and `0.2`.
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P1. Blocks the manifest and the realism work.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-206, FR-207, FR-213
- **issue:** #94

### gen-meta-overwrite

- **title:** Record sidecar transform steps as an ordered list
- **domain:** generation
- **artifact:** `card_identifier/dataset/generator.py:59-65`
- **claim:** The sidecar merges all steps into one dict, so colliding keys keep only the last step.
- **falsifier:** A sidecar from a three-step image lists all three step names.
- **evidence:**
  - `card_identifier/dataset/generator.py:59-65` calls `meta.update` for each step.
  - Reviewer run: keys after one image are `[coefficients, degrees, method, pa, resize, transform, transformer]` with `transformer == "rotate"`.
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P2. Provenance is a stated principle.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-202
- **issue:** #95

### gen-perspective-clip

- **title:** Fix perspective clipping and make card scale independent of the source scan
- **domain:** generation
- **artifact:** `card_identifier/image/transformers.py:77-107`
- **claim:** Perspective moves corners outside the canvas in 64% of draws, and card scale depends on the source scan's size.
- **falsifier:** Over 2,000 seeded draws no corner leaves the working canvas.
- **evidence:**
  - `card_identifier/image/transformers.py:77-107` (wobble 0.2, shift, canvas `1 + wobble_percent`).
  - Reviewer simulation: 1,289 of 2,000 random perspective draws put a corner off the canvas.
  - `card_identifier/dataset/generator.py:69-71` places the rotated card with `limit=0.75` on a 1,024 px canvas.
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P2. Training images lose card edges.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-208, FR-209
- **issue:** #96

### gen-trim-orphans

- **title:** Make trim-dataset remove sidecars and choose files deterministically
- **domain:** generation
- **artifact:** `card_identifier/cli/trim_dataset.py:51-55`
- **claim:** trim-dataset deletes PNGs and leaves their sidecars.
- **falsifier:** After `trim-dataset -n 1` on a card with 3 variants, 1 PNG and 1 JSON remain.
- **evidence:**
  - `card_identifier/cli/trim_dataset.py:51-55` unlinks `image` only.
- **verdict:** CONFIRMED
- **severity:** Low
- **priority:** P2. Leaves junk; low impact.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-215
- **issue:** #97

### docs-data-licensing

- **title:** Document where backgrounds come from, and record each image's source
- **domain:** docs
- **artifact:** ``rg -i background README.md` shows the directory name and no`
- **claim:** Where backgrounds and card images come from, and the terms of use, are not written down.
- **falsifier:** The README names acceptable background sources and says to record their licence.
- **evidence:**
  - `rg -i background README.md` shows the directory name and no source or licence guidance (docs branch).
  - `.gitignore:2` and `.dockerignore:1` list `data/`.
  - Scrydex terms (https://scrydex.com/terms, read 2026-10-09) bar "redistribute, mirror" without authorization and extracting "models… datasets".
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P2. Legal exposure if the repo or weights are ever shared.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-116, NFR-8
- **issue:** #98

### infra-rtm-check

- **title:** Add a check that links tests to requirements
- **domain:** infra
- **artifact:** `docs/rtm.md`
- **claim:** No check keeps the requirement matrix and the tests in step.
- **falsifier:** A script today fails when a spec requirement is missing from the matrix.
- **evidence:**
  - `docs/rtm.md` lists 82 requirements; no script in the repository reads it (`rg ReqID scripts tests` finds nothing).
- **verdict:** CONFIRMED
- **severity:** Low
- **priority:** P3. Keeps the spec system honest.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** NFR-11
- **issue:** #99

### trn-backbone-registry

- **title:** Add a backbone registry with licence checks and a shared preprocessing contract
- **domain:** training
- **artifact:** `Hugging Face model cards read 2026-10-09: `timm/convnextv2_t`
- **claim:** No place records a backbone's weights, input size, normalization and licence, and no shared preprocessing exists.
- **falsifier:** A second backbone can be selected by config today.
- **evidence:**
  - Hugging Face model cards read 2026-10-09: `timm/convnextv2_tiny.fcmae_ft_in22k_in1k` CC-BY-NC-4.0; `timm/mobilenetv4_conv_medium`, `timm/tf_efficientnetv2_s.in21k_ft_in1k`, `google/siglip2-base-patch16-224` Apache-2.0.
  - `notebooks/xfer_model.ipynb` hard-codes MobileNetV2 and `num_classes = 116`.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. Foundation for all architectures.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **ledger row:** split from `trn-trainer`
- **requirements:** FR-402, FR-403, FR-602
- **issue:** #100

### trn-loader

- **title:** Add a manifest-driven dataset class and the train command skeleton
- **domain:** training
- **artifact:** `notebooks/gen_model.ipynb`
- **claim:** No code reads a build manifest for training; the notebooks glob hard-coded directories.
- **falsifier:** A command today trains from a manifest.
- **evidence:**
  - `notebooks/gen_model.ipynb` calls `image_dataset_from_directory` on a hard-coded `/home/...` path.
  - `rg -i 'torch|keras|train' card_identifier` finds nothing.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. All training reads through it.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **ledger row:** split from `trn-trainer`
- **requirements:** FR-401, FR-409, FR-413, FR-414
- **issue:** #101

### trn-embedding-training

- **title:** Train an embedding model with a metric-learning loss
- **domain:** training
- **artifact:** `Prior art read 2026-10-09: `ManuelZ/pairwise-similarity` tra`
- **claim:** The package has no trainer for an embedding model.
- **falsifier:** A command today trains an embedding model and writes a checkpoint.
- **evidence:**
  - Prior art read 2026-10-09: `ManuelZ/pairwise-similarity` trains with Circle Loss on one image per card; `LMilazzo/cardexx` matches CLIP embeddings by cosine.
  - `notebooks/gen_model.ipynb` trains a 3-layer CNN with `Adam(lr=0.000001)` for 500 epochs; its cell 'FIXME: This, below here...' shows it never finished.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. The core capability.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **ledger row:** split from `trn-trainer`
- **requirements:** FR-404, FR-410, FR-411, FR-412, NFR-2, NFR-6
- **issue:** #102

### trn-reference-index

- **title:** Build and query a reference index; add cards without retraining
- **domain:** training
- **artifact:** `TCGdex lists 23,736 card entries on 2026-10-09 (`curl https:`
- **claim:** The package cannot embed reference scans or answer a nearest-neighbour query.
- **falsifier:** A command today embeds reference scans or answers a nearest-neighbour query.
- **evidence:**
  - TCGdex lists 23,736 card entries on 2026-10-09 (`curl https://api.tcgdex.net/v2/en/cards | jq length`), 21,256 of them in physical sets.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P1. Turns a model into an identifier.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **ledger row:** split from `trn-trainer`
- **requirements:** FR-405, FR-406, NFR-2
- **issue:** #103

### trn-classifier-baseline

- **title:** Add a classifier-head baseline on the same data and config
- **domain:** training
- **artifact:** `scripts/run_mkimgclsfr.sh`
- **claim:** No classifier baseline exists to compare with retrieval.
- **falsifier:** A command today trains a classifier on the card ids of a build.
- **evidence:**
  - The old TF Hub path trained a softmax head (`scripts/run_mkimgclsfr.sh` at `eaea9c3`; #78 deletes it); nothing replaces it.
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P2. Gives the comparison a baseline.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **ledger row:** split from `trn-trainer`
- **requirements:** FR-407
- **issue:** #104

### trn-multilabel

- **title:** Report card labels with every identification and add optional attribute heads
- **domain:** training
- **artifact:** ``rg -i 'rarity|regulation' card_identifier` finds no label o`
- **claim:** No code path returns a card's rarity, types, set or regulation mark.
- **falsifier:** Any code path today returns a rarity, type or set for an identified card.
- **evidence:**
  - `rg -i 'rarity|regulation' card_identifier` finds no label other than the card id in any model path (reviewer check).
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P2. A stated requirement, after the core works.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-408
- **issue:** #105

### trn-eval-real

- **title:** Add real-photo evaluation with per-label metrics and reports
- **domain:** evaluation
- **artifact:** `notebooks/xfer_model.ipynb`
- **claim:** Accuracy is only ever measured on synthetic validation images.
- **falsifier:** A command today measures accuracy on photographs of physical cards.
- **evidence:**
  - `notebooks/xfer_model.ipynb` evaluates on `image_dataset_from_directory(..., validation_split=0.2)` of synthetic images only.
  - `rg -i 'real photo|labels.csv|evaluate' card_identifier` finds nothing.
- **verdict:** CONFIRMED
- **severity:** High
- **priority:** P2. The only honest measure of the project.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-501, FR-502, FR-503, FR-505, FR-506, FR-507, NFR-2
- **issue:** #106

### trn-approach-compare

- **title:** Compare retrieval and classifier approaches across backbones
- **domain:** evaluation
- **artifact:** `No comparison exists: the package has no trainer.`
- **claim:** The choice of retrieval over a classifier rests on prior art, not on a measurement here.
- **falsifier:** The classifier baseline beats retrieval on real photos at equal training budget.
- **evidence:**
  - No comparison exists: the package has no trainer.
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P2. Settles the main design bet.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-504
- **issue:** #107

### inf-cli-export

- **title:** Add an identify command and an ONNX bundle export
- **domain:** inference
- **artifact:** `scripts/label_image.py:55-57`
- **claim:** No command identifies a card from a photo; the only inference script is a TensorFlow Lite sample with wrong defaults.
- **falsifier:** A command today prints a card id for a photo.
- **evidence:**
  - `scripts/label_image.py:55-57` (at `eaea9c3`; #78 deletes it) defaults `input_mean` and `input_std` to 127.5; `:108` opens the image and resizes with no `convert`.
  - `pyproject.toml:48` excludes the script from pyright; `tests/test_label_image.py` calls `--help` only and is skipped when TensorFlow is missing.
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P2. Delivers the usable identifier.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-601, FR-602, FR-603, FR-604, FR-605, NFR-2
- **issue:** #108

### gen-realism

- **title:** Add camera-realistic transforms (glare, blur, lighting, JPEG, sleeves, occlusion)
- **domain:** generation
- **artifact:** `card_identifier/image/transformers.py`
- **claim:** Generated images lack glare, blur, lighting, JPEG artifacts, sleeve reflections and occlusion.
- **falsifier:** Generated images contain glare, blur or compression artifacts today.
- **evidence:**
  - `card_identifier/image/transformers.py` defines noise, resize, perspective, rotate, autocontrast, posterize and solarize only.
  - `rg -i 'glare|blur|jpeg|occlu' card_identifier` finds nothing (reviewer check).
- **verdict:** CONFIRMED
- **severity:** Medium
- **priority:** P2. Improves transfer to real photos; after the baseline works.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** FR-214
- **issue:** #109

### misc-stale-experiments

- **title:** Fix or remove the Streamlit demo and the stale notebooks
- **domain:** infra
- **artifact:** `scripts/streamlit/foo.py:13`
- **claim:** The Streamlit demo reads attributes that do not exist, and the notebooks hard-code personal paths.
- **falsifier:** `streamlit run scripts/streamlit/foo.py` runs without error against a current catalog.
- **evidence:**
  - `scripts/streamlit/foo.py:13` uses `card_set.logo_url` (the SDK `Set` has `images.logo`), `:16` calls `int(c.number)` on card id strings, `:18` uses `card.image_url`.
  - `notebooks/gen_model.ipynb`, `xfer_model.ipynb`: `data_dir = pathlib.Path('/home/ravenoak/...')`.
- **verdict:** CONFIRMED
- **severity:** Low
- **priority:** P3. Cleanup.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** none
- **issue:** #110

### misc-version-dup

- **title:** Single-source the package name and version
- **domain:** infra
- **artifact:** `card_identifier/config.py:7-8`
- **claim:** The version and package name are written in two files.
- **falsifier:** A release bumps one file and the other follows by itself.
- **evidence:**
  - `card_identifier/config.py:7-8`; `pyproject.toml:3`.
- **verdict:** CONFIRMED
- **severity:** Low
- **priority:** P4. Trivial.
- **dedup_check:** none found (`gh issue list --state all` returned `[]` on 2026-10-09)
- **disposition:** file
- **requirements:** none
- **issue:** #111

### Routed without an issue

#### infra-local-ci

- **title:** Pre-commit hook runs tests in parallel with -n auto
- **domain:** infra
- **artifact:** prek.toml:42
- **claim:** `prek.toml:42` runs `pytest -n auto` at commit time, which `local-ci-standard.md` Requirement 2 forbids ('Never `-n auto`').
- **falsifier:** The standard applies to this repository.
- **evidence:** Reviewer read `prek.toml:42` and `local-ci-standard.md:18-20`. `CLAUDE.md` and `AGENTS.md` of this repository require `uv run pytest -n auto`, and the repository is not in the standard's audited list.
- **verdict:** CONFIRMED
- **severity:** Low
- **disposition:** hold
- **note:** The standard targets repositories that share a private-repo quota and one machine. Owner may promote this to an issue.

## Verification

A second model (Sonnet 5.5) tried to refute each finding, and did not write the findings it
checked. It ran the repro for `gen-json-crash`, `cat-card-parse`, `gen-repro` and
`gen-failure-isolation`, read the code for the rest, and searched for the absent features
named in the feature rows. Results: 27 CONFIRMED, 3 ESCALATE, 0 CLEARED. The three ESCALATE rows
were resolved by the examiner:

- `sel-legal-semantics`: the code claim holds. The rotation date comes from a news source,
  so the issue relies on the per-card legality flags instead of the date.
- `gen-realism`: the scale claim is only partly checked (see below).
- `sel-symlinks-dir`: confirmed by code reading. The filesystem repro is the first test in the
  issue.

Corrections the verifier made, now applied: `gen-failure-isolation` aborts one worker chunk,
not the whole run, and exits 1 with a traceback. The `cat-card-parse` impact is total, not
limited to new sets. `inf-cli-export`: the 127.5 normalization is a default, not hard-coded.
`docs-training-drift`: the namespace path half is overstated.

### Reproductions

`gen-json-crash`: a 734x1024 RGBA PNG, one JPEG in the backgrounds directory, seeds 0 to 4:
5 of 5 runs raise `TypeError: Object of type ndarray is not JSON serializable`, each leaving a
PNG and a sidecar cut off at `"coefficients": `.

`gen-repro`: `random.seed(42)` in the parent, `Pool(2).starmap(random_rotate)` under `spawn`:
run 1 `[194, 269, 333, 110]`, run 2 `[257, 74, 355, 66]`.

`gen-perspective-clip`: 1,289 of 2,000 random perspective draws put a corner off the canvas.

## Counts and the commands that produce them

| Count | Command | Ref |
|---|---|---|
| 42 passed, 1 skipped | `uv run pytest -n auto -q` | `main` at `eaea9c3` |
| 176 pokemon-tcg-data sets, 220 TCGdex sets, 126 shared ids | `gh api repos/PokemonTCG/pokemon-tcg-data/contents/sets/en.json`, `curl https://api.tcgdex.net/v2/en/sets`, then compare `id` fields | live, 2026-10-09 |
| Set totals: 20,530 pokemon-tcg-data; 23,964 TCGdex, of which 21,484 in 205 physical sets | sum of `total` / `cardCount.total` in the set lists above; physical = all sets except series `tcgp` (`curl https://api.tcgdex.net/v2/en/series/tcgp`) | live, 2026-10-09 |
| 23,736 TCGdex card entries | `curl https://api.tcgdex.net/v2/en/cards \| jq length` | live, 2026-10-09 |
| 83 requirements | `python3 -I` over `docs/specs/*.md` counting `**FR-N.**` and `**NFR-N.**` | this branch |
| 37 issues | `gh issue list --state all --limit 200 --json number \| jq length` | live, 2026-10-09, after filing (#75 to #111) |

## Limits

- No real card images were available on disk, so source-scan size was measured on one file
  (Scrydex `me55c-58`, 654x914). TCGdex `high` (600x825) comes from its documentation. The
  crosswalk spike measures all sources.
- The pokemontcg.io API returned HTTP 500 at 2026-10-10 06:00 UTC and 200 at 06:39, so cards from the live API were
  never parsed. `cat-card-parse` rests on the SDK source, the payload in `pokemon-tcg-data`, and the
  verifier's patched-client repro.
- TensorFlow and PyTorch were not installed. Claims about wheels come from PyPI metadata read on
  2026-10-09.
- The Dockerfiles were read, not built.
- Notebook outputs were not examined, only their code cells.
- No GPU, no Apple-silicon performance measurement, and no training run were possible, because no
  trainer exists.
- The rotation date for Standard (H, I and J legal after 2026-04-10) comes from a news article
  (pokeguardian.com, 2026-01-09), not from an official Pokemon source.
- TCGdex rate limits and image terms were not found in its documentation. The spike should
  look again.
- Image rights: no source reviewed grants rights to card images. This is a risk statement, not a legal opinion.

## Review of the filed backlog

A second reviewer (Sonnet 5.5) checked the pull request and the 37 issues after filing. It
confirmed all cited line numbers and found defects in claims, structure and wording. Applied:

- Canonical ids. 4,056 of 23,736 TCGdex card ids broke the id rule (2,480 are TCG Pocket cards,
  1,576 are physical cards with upper case or punctuation such as `pl4-AR1` and `exu-!`). The rule
  now keeps ids as written and derives file names with `file_name(id)` (NFR-7). TCG Pocket is left
  out (FR-117). Card counts are compared as set totals.
- Requirements. FR-307 (shared pool keyed by config hash and seed), FR-308 (check no longer
  contradicts a hash split), FR-310 and FR-603 (distinct commands `export-imagefolder` and
  `export-bundle`), NFR-3 (the random-state pickles go away in the reproducibility issue), FR-206
  and FR-213 (manifest recording belongs to FR-306), and vague terms in FR-401, FR-404, FR-408,
  FR-603.
- Issues. Missing blocked-by edges added, one hidden cycle removed, two priority inversions fixed
  (the label catalog is now P0 and the generator config P1), requirement links aligned with the
  matrix, one stale issue rewritten, wrong claims corrected (the symlink bug appears on the first
  run; the API fails intermittently).
- Not applied: the style comment on long sentences in requirements. Requirements keep their one-sentence form.

## Sources

- pokemon-tcg-data README, commit 2026-09-17: API offline 2027-03-01.
- PyPI JSON for `pokemontcgsdk`, `tensorflow`, `tensorflow-hub`, `keras`, `torch`, read 2026-10-09.
- tensorflow/hub release notes v0.14.0 (2023-07-13).
- https://scrydex.com/faq, /pricing, /terms. https://tcgdex.dev/ and https://github.com/tcgdex/cards-database.
- https://github.com/LMilazzo/cardexx, https://github.com/ManuelZ/pairwise-similarity.
- Hugging Face model cards for the backbone licences listed in ADR 0002.
