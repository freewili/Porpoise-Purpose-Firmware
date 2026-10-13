# Porpoise Purpose module release format (schema 1)

The folder `releases/<tag>/`, GitHub tag, manifest `release`, and
`Porpoise-Purpose-<tag>.zip` share one identity. Tags match
`v[0-9][A-Za-z0-9.-]*` and are at most 80 characters. Published tags and assets
must never be replaced; corrections use a new tag.

Each release contains exactly `README.md`, `manifest.json`, and
`firmware/Porpoise-Purpose.uf2`. The manifest has `schema: 1`,
`product: "Porpoise-Purpose"`, `release`, `title`, and a single `files` record with
`component: "main"`, `version` (the image's `v` version), `file`, `size`, and
lowercase `sha256`. Optional `source` records build provenance. Mark modified
source builds `dirty: true`; a base revision alone cannot reproduce them.

`scripts/package_release.py releases/<tag>` validates UF2 magic, RP2350 ARM
family, block completeness, board identity, version, flash bounds, and SHA-256.
Only the exact picotool RP2350-E10 workaround record may lie outside the lower
8 MiB firmware area. The ZIP uses fixed timestamps and permissions.

The publish workflow runs tests and creates four assets: the ZIP, its `.sha256`,
the identical standalone UF2, and `checksums-<tag>.txt`. It creates a draft,
uploads all assets, then publishes. Choose **preview** or **stable** explicitly.
CI validates all committed release folders on Windows, macOS, and Linux.
Packaging checks do not establish actual hardware behavior; release notes
must state which device tests were run.
