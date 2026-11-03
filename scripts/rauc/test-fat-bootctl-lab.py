#!/usr/bin/env python3
"""Integration tests using a genuine copied BOOTCTL FAT image."""

import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).with_name(
    "secureedge-fat-bootctl-lab.py"
).resolve()

SOURCE = Path(
    "/mnt/secureedge-storage/rauc-ab-tests/"
    "phase11-fat-integration/bootctl-original.vfat"
)


def run(*args):
    return subprocess.run(
        args, capture_output=True, text=True
    )


def mtype(image):
    result = run(
        "mtype", "-i", str(image), "::autoboot.txt"
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def mcopy(image, content):
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "autoboot.txt"
        source.write_text(content)

        result = run(
            "mcopy", "-o", "-i", str(image),
            str(source), "::autoboot.txt"
        )
        assert result.returncode == 0, result.stderr


if not SOURCE.is_file():
    sys.exit("BLOCKED: extracted BOOTCTL image missing")

with tempfile.TemporaryDirectory(
    prefix="secureedge-fat-",
    dir="/tmp"
) as directory:

    root = Path(directory)
    (root / ".secureedge-fat-lab").touch()

    original = root / "bootctl-original.vfat"
    original.write_bytes(SOURCE.read_bytes())

    initial = mtype(original)
    assert "boot_partition=2" in initial

    result = run(
        "python3", str(TOOL),
        "--lab-root", str(root),
        "--target", "system1",
    )

    assert result.returncode == 0, result.stderr
    assert "FAT_CONFIRMATION=PASS" in result.stdout

    candidate = root / "bootctl-candidate.vfat"
    confirmed = mtype(candidate)

    assert "boot_partition=3" in confirmed
    print("PASS: actual FAT A -> B")

    reverse = root / "reverse"
    reverse.mkdir()
    (reverse / ".secureedge-fat-lab").touch()

    (reverse / "bootctl-original.vfat").write_bytes(
        candidate.read_bytes()
    )

    result = run(
        "python3", str(TOOL),
        "--lab-root", str(reverse),
        "--target", "system0",
    )

    assert result.returncode == 0, result.stderr
    assert "FAT_CONFIRMATION=PASS" in result.stdout

    restored = mtype(
        reverse / "bootctl-candidate.vfat"
    )

    assert restored == initial
    print("PASS: actual FAT B -> A")

    broken = root / "broken"
    broken.mkdir()
    (broken / ".secureedge-fat-lab").touch()

    broken_image = broken / "bootctl-original.vfat"
    broken_image.write_bytes(SOURCE.read_bytes())

    mcopy(
        broken_image,
        "[all]\nboot_partition=99\n"
    )

    result = run(
        "python3", str(TOOL),
        "--lab-root", str(broken),
        "--target", "system1",
    )

    assert result.returncode != 0
    assert not (
        broken / "bootctl-candidate.vfat"
    ).exists()

    print("PASS: corrupt BOOTCTL rejected")

print("PHASE_11_FAT_INTEGRATION=PASS")
print("HARDWARE_OTA=NO-GO")
