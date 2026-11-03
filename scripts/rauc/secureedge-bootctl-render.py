#!/usr/bin/env python3
"""Offline-only BOOTCTL A/B confirmation renderer."""

import argparse
import sys
from pathlib import Path

PARTITIONS = {
    "system0": 2,
    "system1": 3,
}


def render(source, current, target):
    if current not in PARTITIONS or target not in PARTITIONS:
        raise ValueError("Invalid slot")

    if current == target:
        raise ValueError("Target must differ from primary")

    expected = (
        "[all]\n"
        "tryboot_a_b=1\n"
        f"boot_partition={PARTITIONS[current]}\n"
        "\n"
        "[tryboot]\n"
        f"boot_partition={PARTITIONS[target]}\n"
    )

    if source.replace("\r\n", "\n") != expected:
        raise ValueError("Unexpected BOOTCTL configuration")

    return (
        "[all]\n"
        "tryboot_a_b=1\n"
        f"boot_partition={PARTITIONS[target]}\n"
        "\n"
        "[tryboot]\n"
        f"boot_partition={PARTITIONS[current]}\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("current")
    parser.add_argument("target")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()

    if source_path == Path("/bootctl") or (
        Path("/bootctl") in source_path.parents
    ):
        raise ValueError("Live BOOTCTL forbidden")

    if source_path.is_symlink():
        raise ValueError("Symlink forbidden")

    result = render(
        source_path.read_text(encoding="ascii"),
        args.current,
        args.target,
    )

    sys.stdout.write(result)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, UnicodeError) as exc:
        sys.exit(f"BOOTCTL ERROR: {exc}")
