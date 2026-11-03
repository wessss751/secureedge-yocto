#!/usr/bin/env python3
"""Read-only offline inspection of a SecureEdge BOOTCTL transaction."""

import argparse
import hashlib
import json
from pathlib import Path


def decision(code, detail, success=False):
    print(f"RECOVERY_DECISION={code}")
    print(f"DETAIL={detail}")
    print("REAL_BOOTCTL_WRITES=NO")
    raise SystemExit(0 if success else 2)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def render(primary, alternate):
    return (
        "[all]\n"
        "tryboot_a_b=1\n"
        f"boot_partition={primary}\n\n"
        "[tryboot]\n"
        f"boot_partition={alternate}\n"
    ).encode("ascii")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-root", required=True)
    args = parser.parse_args()

    root = Path(args.lab_root).absolute()

    if root.is_symlink() or root.resolve() in (
        Path("/"),
        Path("/bootctl"),
        Path("/data"),
    ):
        decision("BLOCKED", "Unsafe laboratory root")

    marker = root / ".secureedge-offline-lab"
    if not marker.is_file() or marker.is_symlink():
        decision("BLOCKED", "Missing laboratory marker")

    output = root / "output"
    journal_file = output / "confirmation.json"
    bootctl_file = output / "autoboot.txt"

    for path in (output, journal_file, bootctl_file):
        if path.is_symlink():
            decision("BLOCKED", "Symlink rejected")

    if not journal_file.is_file() or not bootctl_file.is_file():
        decision("BLOCKED", "Incomplete transaction evidence")

    try:
        raw = journal_file.read_bytes()
        journal = json.loads(raw)
        current = bootctl_file.read_bytes()
    except (OSError, ValueError):
        decision("BLOCKED", "Cannot read transaction")

    if not isinstance(journal, dict):
        decision("BLOCKED", "Invalid journal structure")

    if journal.get("schema") != 1:
        decision("BLOCKED", "Unsupported journal schema")

    if journal.get("mode") != "offline-lab":
        decision("BLOCKED", "Not an offline transaction")

    state = journal.get("status")
    if state not in ("prepared", "committed"):
        decision("BLOCKED", "Unknown transaction state")

    old = journal.get("previous_primary_partition")
    new = journal.get("new_primary_partition")
    candidate = journal.get("candidate")

    if (old, new, candidate) not in (
        ("2", "3", "system1"),
        ("3", "2", "system0"),
    ):
        decision("BLOCKED", "Invalid slot mapping")

    old_data = render(old, new)
    new_data = render(new, old)

    old_hash = journal.get("source_sha256")
    new_hash = journal.get("new_sha256")

    if not isinstance(old_hash, str) or not isinstance(new_hash, str):
        decision("BLOCKED", "Missing transaction digests")

    if sha256(new_data) != new_hash:
        decision("BLOCKED", "New configuration digest mismatch")

    is_old = sha256(current) == old_hash
    is_new = current == new_data and sha256(current) == new_hash

    if is_old and is_new:
        decision("BLOCKED", "Ambiguous transaction state")

    if state == "prepared":
        if is_old:
            decision(
                "KEEP_OLD_PRIMARY",
                "Confirmation not applied; do not retry automatically",
                True,
            )
        if is_new:
            decision(
                "VERIFY_BEFORE_FINALIZE",
                "New configuration present, journal not committed",
                True,
            )

    if state == "committed" and is_new:
        decision(
            "CONSISTENT",
            "New primary matches committed journal",
            True,
        )

    if state == "committed" and is_old:
        decision(
            "BLOCKED",
            "Committed journal conflicts with old BOOTCTL",
        )

    decision(
        "BLOCKED",
        "BOOTCTL does not match either expected transaction state",
    )


if __name__ == "__main__":
    main()
