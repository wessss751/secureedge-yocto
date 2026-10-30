
#!/usr/bin/env python3
"""SecureEdge boot evidence collector (read-only prototype)."""

import argparse
import json
import re
from pathlib import Path


def read_firmware_u32(path):
    data = Path(path).read_bytes()
    if len(data) != 4:
        raise ValueError(f"Invalid firmware property: {path}")
    return int.from_bytes(data, "big")


def read_autoboot(path):
    sections = {}
    section = None

    for raw in Path(path).read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        if re.fullmatch(r"\[[A-Za-z0-9_-]+\]", line):
            section = line[1:-1]
            if section in sections:
                raise ValueError("Duplicate autoboot section")
            sections[section] = {}
            continue

        if "=" not in line or section is None:
            raise ValueError("Malformed autoboot configuration")

        key, value = (part.strip() for part in line.split("=", 1))
        if not key or not value or key in sections[section]:
            raise ValueError("Invalid or duplicate autoboot key")

        sections[section][key] = value

    if sections.get("all", {}).get("tryboot_a_b") != "1":
        raise ValueError("A/B tryboot mode not enabled")

    normal = int(sections["all"]["boot_partition"])
    trial = int(sections["tryboot"]["boot_partition"])

    if {normal, trial} != {2, 3}:
        raise ValueError("Unexpected boot partition mapping")

    return normal, trial


def read_current_slot(path):
    args = Path(path).read_text().split()
    slots = [arg.split("=", 1)[1]
             for arg in args if arg.startswith("rauc.slot=")]
    roots = [arg.split("=", 1)[1]
             for arg in args if arg.startswith("root=")]

    if len(slots) != 1 or len(roots) != 1:
        raise ValueError("Ambiguous kernel cmdline")

    slot = slots[0]
    expected_root = {
        "system0": "/dev/mmcblk0p5",
        "system1": "/dev/mmcblk0p6",
    }

    if slot not in expected_root or roots[0] != expected_root[slot]:
        raise ValueError("Slot/rootfs mismatch")

    return slot


def collect(base):
    base = Path(base)
    normal, trial = read_autoboot(base / "bootctl/autoboot.txt")
    current = read_current_slot(base / "proc/cmdline")

    firmware = base / "proc/device-tree/chosen/bootloader"
    tryboot = read_firmware_u32(firmware / "tryboot")
    partition = read_firmware_u32(firmware / "partition")

    if tryboot not in (0, 1):
        raise ValueError("Invalid tryboot flag")

    expected_partition = trial if tryboot else normal
    if partition != expected_partition:
        raise ValueError("Firmware/autoboot mismatch")

    expected_slot = {2: "system0", 3: "system1"}[partition]
    if current != expected_slot:
        raise ValueError("Firmware/current slot mismatch")

    return {
        "current": current,
        "primary": {2: "system0", 3: "system1"}[normal],
        "tryboot_target": {2: "system0", 3: "system1"}[trial],
        "tryboot": tryboot,
        "firmware_partition": partition,
        "health_verified": False,
        "confirmation_authorized": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/")
    args = parser.parse_args()

    try:
        result = collect(args.root)
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({
            "error": str(exc),
            "confirmation_authorized": False,
        }))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
