#!/usr/bin/env python3
"""Read-only parser for SecureEdge Raspberry Pi autoboot.txt."""

from pathlib import Path


class BootctlError(ValueError):
    pass


PARTITION_TO_SLOT = {
    2: "system0",
    3: "system1",
}


def read_bootctl(path):
    path = Path(path)

    if not path.is_file():
        raise BootctlError("autoboot.txt is missing")

    sections = {}
    section = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line in ("[all]", "[tryboot]"):
            if line in sections:
                raise BootctlError("Duplicate section")
            section = line
            sections[section] = {}
            continue

        if section is None or "=" not in line:
            raise BootctlError("Unexpected BOOTCTL syntax")

        key, value = (part.strip() for part in line.split("=", 1))

        if key not in ("tryboot_a_b", "boot_partition"):
            raise BootctlError("Unsupported BOOTCTL key")

        if key in sections[section]:
            raise BootctlError("Duplicate BOOTCTL key")

        if not value.isdecimal():
            raise BootctlError("Non-numeric BOOTCTL value")

        sections[section][key] = int(value)

    normal = sections.get("[all]", {})
    trial = sections.get("[tryboot]", {})

    if normal.get("tryboot_a_b") != 1:
        raise BootctlError("tryboot_a_b must be enabled")

    if set(normal) != {"tryboot_a_b", "boot_partition"}:
        raise BootctlError("Invalid normal section")

    if set(trial) != {"boot_partition"}:
        raise BootctlError("Invalid tryboot section")

    primary_partition = normal["boot_partition"]
    trial_partition = trial["boot_partition"]

    if primary_partition not in PARTITION_TO_SLOT:
        raise BootctlError("Invalid primary partition")

    if trial_partition not in PARTITION_TO_SLOT:
        raise BootctlError("Invalid trial partition")

    if primary_partition == trial_partition:
        raise BootctlError("Primary and trial partitions must differ")

    return {
        "primary": PARTITION_TO_SLOT[primary_partition],
        "trial": PARTITION_TO_SLOT[trial_partition],
        "primary_partition": primary_partition,
        "trial_partition": trial_partition,
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: bootctl_reader.py AUTOboot.txt")

    try:
        print(json.dumps(read_bootctl(sys.argv[1]), indent=2))
    except (BootctlError, OSError, UnicodeError) as exc:
        raise SystemExit(f"BOOTCTL ERROR: {exc}")
