
#!/usr/bin/env python3
"""SecureEdge offline boot layout validator.

Read-only. Operates on a supplied test directory.
"""

import argparse
import json
import re
from pathlib import Path


def parse_autoboot(path):
    sections = {}
    current = None

    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        if re.fullmatch(r"\[(all|tryboot)\]", line):
            current = line[1:-1]
            if current in sections:
                raise ValueError("Duplicate section")
            sections[current] = {}
            continue

        if current is None or line.count("=") != 1:
            raise ValueError("Malformed autoboot.txt")

        key, value = map(str.strip, line.split("=", 1))
        if not key or not value or key in sections[current]:
            raise ValueError("Invalid or duplicate setting")
        sections[current][key] = value

    if set(sections) != {"all", "tryboot"}:
        raise ValueError("Missing boot sections")

    if sections["all"] != {
        "tryboot_a_b": "1",
        "boot_partition": sections["all"].get("boot_partition"),
    }:
        raise ValueError("Unexpected normal boot directives")

    if set(sections["tryboot"]) != {"boot_partition"}:
        raise ValueError("Unexpected trial boot directives")

    normal = sections["all"]["boot_partition"]
    trial = sections["tryboot"]["boot_partition"]

    if {normal, trial} != {"2", "3"}:
        raise ValueError("Invalid A/B mapping")

    return int(normal), int(trial)


def check_cmdline(path, slot, root):
    args = path.read_text().split()

    slot_values = [
        item.split("=", 1)[1]
        for item in args if item.startswith("rauc.slot=")
    ]
    root_values = [
        item.split("=", 1)[1]
        for item in args if item.startswith("root=")
    ]

    if slot_values != [slot]:
        raise ValueError(f"Invalid rauc.slot in {path}")

    if root_values != [root]:
        raise ValueError(f"Invalid root device in {path}")


def validate(base):
    base = Path(base).resolve()

    bootctl = base / "BOOTCTL"
    boot_a = base / "BOOT_A"
    boot_b = base / "BOOT_B"

    normal, trial = parse_autoboot(bootctl / "autoboot.txt")

    for directory, slot, root in (
        (boot_a, "system0", "/dev/mmcblk0p5"),
        (boot_b, "system1", "/dev/mmcblk0p6"),
    ):
        for filename in (
            "kernel8.img",
            "config.txt",
            "bcm2710-rpi-zero-2.dtb",
            "cmdline.txt",
        ):
            path = directory / filename

            if path.is_symlink() or not path.is_file():
                raise ValueError(f"Missing or unsafe file: {path}")

            if path.stat().st_size == 0:
                raise ValueError(f"Empty boot file: {path}")

        check_cmdline(directory / "cmdline.txt", slot, root)

    return {
        "valid": True,
        "normal_partition": normal,
        "trial_partition": trial,
        "boot_a": "validated_static_layout",
        "boot_b": "validated_static_layout",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()

    try:
        result = validate(args.root)
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
