# Porpoise Purpose module v1

Initial downloadable stock firmware package for the Porpoise Purpose module.
Built from firmware main revision `0aa12fb1121f8108f21f9e6d870607f3055385e2` using Pico SDK 2.3.0 and
Arm GNU 14.2.Rel1, Release configuration.

Validated: firmware build, complete RP2350 UF2 structure, board identity,
version, flash address bounds, manifest size, and SHA-256 checksums.
These checks do not establish hardware operation. This publication has not
been flash-tested on a physical Porpoise Purpose module, or through the GUI on macOS/Linux.

Use **Tools > Firmware Update > Porpoise Purpose module** in a GUI build containing the
new updater, or copy the standalone UF2 to this board's RP2350 BOOTSEL drive.
Keep USB power connected. Internal data and microSD contents are preserved.
