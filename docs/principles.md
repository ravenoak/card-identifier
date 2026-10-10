# Principles

These rules apply to every spec and every pull request. Each has a reason and a place where it
is enforced or will be.

1. **Same inputs, same outputs.** A build from the same selection, config and seed produces the
   same files, whatever the number of worker processes. Randomness comes from an explicit
   seeded generator, never from global state. Enforced by [FR-204](specs/generation.md).
2. **Every artifact records where it came from.** Catalogs, builds, models, indexes and
   reports carry the code version, config hash, seed and input hashes. A file with no
   provenance cannot be trusted or compared. Enforced by [NFR-2](specs/nfr.md).
3. **Core is game-agnostic.** The core imports no game module. A game supplies a source
   adapter, a label schema extension and a legality rule, and one registry entry. Enforced by
   [FR-115](specs/catalog.md) and [NFR-9](specs/nfr.md).
4. **No network or disk work in constructors.** Building an object is cheap and has no side
   effects. Commands do the work. Enforced by [FR-113](specs/catalog.md).
5. **Persisted data outlives the code.** Catalogs, manifests, sidecars and indexes use plain
   formats (JSON, JSON Lines, Parquet, NumPy) that other tools read. No pickle. A pickle from a
   shared or old file runs code on load, and it breaks when a class moves. Enforced by
   [NFR-3](specs/nfr.md).
6. **Tests run the real thing.** A test may fake the network and the process pool. It may not
   fake the transform chain, the serializer or the file layout, because the bugs live there.
   One unit test stubbed the perspective transform and hid a crash that stopped every image.
   Enforced by [NFR-5](specs/nfr.md).
7. **Downloaded data is untrusted.** Images and API payloads are validated before use. File
   names come from validated ids. Every request has a timeout. Enforced by
   [NFR-4 and NFR-7](specs/nfr.md).
8. **One failure does not hide the rest.** A bad card, image or file is recorded and skipped.
   The command finishes, prints a summary, and exits non-zero if anything failed. Enforced by
   [FR-103](specs/catalog.md) and [FR-211](specs/generation.md).
9. **Measure on real photos.** A number from synthetic validation images is a training
   signal, not a result. Reports label it so. Enforced by [FR-505](specs/evaluation.md).
10. **Build the least that meets the requirement.** No option, layer or abstraction without a
    requirement that needs it. Brute-force search over 25,000 vectors is fine until a
    measurement says otherwise.
11. **Change specs before behavior.** A pull request that changes behavior changes the spec
    and `rtm.md` in the same diff. See [README](README.md).
