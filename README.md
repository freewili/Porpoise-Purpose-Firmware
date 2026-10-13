# Porpoise Purpose module firmware

Official stock firmware releases for the **Porpoise Purpose module**.

Open **Tools > Firmware Update > Porpoise Purpose module** in a version of FreeWili GUI
that includes this updater. The GUI downloads and validates the selected
release automatically. Select your board, then press **Update and verify**.
Keep USB connected until the board restarts. The updater preserves the internal
data partition and microSD contents.

[Download releases](https://github.com/freewili/Porpoise-Purpose-Firmware/releases).
Stable and Preview are separate channels; Preview builds are marked as GitHub
prereleases. Read each release's verification notes before installing.

Manual recovery: enter the board's RP2350 BOOTSEL mode and copy the standalone
UF2 asset to its recovery drive. Confirm the board model first: other RP2350
boards also expose this drive. These images are only for the Porpoise Purpose module.

This repository contains firmware binaries, release manifests, documentation,
and packaging tools. See [RELEASE_FORMAT.md](RELEASE_FORMAT.md) for publishing.
