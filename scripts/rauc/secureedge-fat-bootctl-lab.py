#!/usr/bin/env python3
"""Offline BOOTCTL FAT integration. Never operates on block devices."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def fail(message):
    raise SystemExit("BLOCKED: " + message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        fail(
            "mtools failed: "
            + result.stderr.strip()
        )
    return result


def parse(data):
    try:
        content = data.decode("ascii")
    except UnicodeDecodeError:
        fail("BOOTCTL is not ASCII")

    sections = {}
    current = None

    for raw in content.splitlines():
        line = raw.strip()

        if not line:
            continue

        if line in ("[all]", "[tryboot]"):
            if line in sections:
                fail("Duplicate section")
            sections[line] = {}
            current = line
            continue

        if current is None or line.count("=") != 1:
            fail("Unexpected BOOTCTL syntax")

        key, value = [
            item.strip()
            for item in line.split("=", 1)
        ]

        if key in sections[current]:
            fail("Duplicate key")

        sections[current][key] = value

    if set(sections) != {"[all]", "[tryboot]"}:
        fail("Unexpected BOOTCTL sections")

    normal = sections["[all]"]
    trial = sections["[tryboot]"]

    if set(normal) != {"tryboot_a_b", "boot_partition"}:
        fail("Unexpected normal properties")

    if set(trial) != {"boot_partition"}:
        fail("Unexpected trial properties")

    if normal["tryboot_a_b"] != "1":
        fail("tryboot_a_b disabled")

    primary = normal["boot_partition"]
    candidate = trial["boot_partition"]

    if (primary, candidate) not in (
        ("2", "3"),
        ("3", "2"),
    ):
        fail("Invalid A/B pairing")

    return primary, candidate


def render(primary, trial):
    return (
        "[all]\n"
        "tryboot_a_b=1\n"
        f"boot_partition={primary}\n\n"
        "[tryboot]\n"
        f"boot_partition={trial}\n"
    ).encode("ascii")


def fat_read(image):
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "autoboot.txt"

        run([
            "mcopy",
            "-i", str(image),
            "::autoboot.txt",
            str(output),
        ])

        return output.read_bytes()


def fat_write(image, content):
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "autoboot.txt"
        source.write_bytes(content)

        run([
            "mcopy",
            "-o",
            "-i", str(image),
            str(source),
            "::autoboot.txt",
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-root", required=True)
    parser.add_argument(
        "--target",
        choices=("system0", "system1"),
        required=True,
    )
    args = parser.parse_args()

    root = Path(args.lab_root).absolute()

    if root.is_symlink():
        fail("Lab directory symlink forbidden")

    resolved = root.resolve()

    if not (
        resolved == Path("/tmp")
        or Path("/tmp") in resolved.parents
    ):
        fail("Only /tmp laboratory directories supported")

    marker = root / ".secureedge-fat-lab"
    original = root / "bootctl-original.vfat"
    output = root / "bootctl-candidate.vfat"
    report = root / "fat-confirmation.json"

    if not marker.is_file() or marker.is_symlink():
        fail("Laboratory marker missing")

    for path in (original, output, report):
        if path.is_symlink():
            fail("Symlink forbidden")
        if path.exists() and not path.is_file():
            fail("Unexpected path type")

    if not original.is_file():
        fail("Original BOOTCTL image missing")

    if original.stat().st_size != 64 * 1024 * 1024:
        fail("Unexpected BOOTCTL image size")

    if output.exists() or report.exists():
        fail("Existing transaction output")

    original_data = fat_read(original)
    old_primary, old_trial = parse(original_data)

    target_partition = (
        "2" if args.target == "system0" else "3"
    )

    if target_partition != old_trial:
        fail("Target must be current trial partition")

    updated = render(old_trial, old_primary)

    shutil.copyfile(original, output)

    fat_write(output, updated)

    readback = fat_read(output)

    if readback != updated:
        fail("FAT readback mismatch")

    new_primary, new_trial = parse(readback)

    if (new_primary, new_trial) != (
        old_trial,
        old_primary,
    ):
        fail("Confirmed partition mapping incorrect")

    evidence = {
        "schema": 1,
        "mode": "offline-fat-lab",
        "old_primary": old_primary,
        "old_trial": old_trial,
        "new_primary": new_primary,
        "new_trial": new_trial,
        "old_config_sha256": digest(original_data),
        "new_config_sha256": digest(readback),
        "output_image": str(output),
        "hardware_qualified": False,
    }

    report.write_text(
        json.dumps(evidence, indent=2) + "\n"
    )

    print("FAT_CONFIRMATION=PASS")
    print(f"OLD_PRIMARY={old_primary}")
    print(f"NEW_PRIMARY={new_primary}")
    print("FAT_READBACK=PASS")
    print("REAL_BOOTCTL_WRITES=NO")
    print("POWERLOSS_QUALIFIED=NO")


if __name__ == "__main__":
    main()
