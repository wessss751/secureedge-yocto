#!/usr/bin/env python3
"""Offline BOOTCTL confirmation transaction. Never writes to real BOOTCTL."""

import argparse
import fcntl
import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path


def fail(message):
    raise SystemExit("BLOCKED: " + message)


def durable_write(path, data):
    """Atomic file replacement within the laboratory filesystem."""
    fd, tmp = tempfile.mkstemp(prefix=".txn-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def parse_autoboot(data):
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError:
        fail("autoboot.txt must be ASCII")

    sections = {}
    section = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line not in ("[all]", "[tryboot]") and (
            line.startswith("[") or line.startswith("#")
        ):
            fail("Unexpected section or comment")

        if line in ("[all]", "[tryboot]"):
            section = line
            if section in sections:
                fail("Duplicate section")
            sections[section] = {}
            continue

        if section is None or line.count("=") != 1:
            fail("Malformed configuration")

        key, value = [part.strip() for part in line.split("=", 1)]
        if key in sections[section]:
            fail("Duplicate key")
        sections[section][key] = value

    if set(sections) != {"[all]", "[tryboot]"}:
        fail("Missing section")

    normal = sections["[all]"]
    trial = sections["[tryboot]"]

    if set(normal) != {"tryboot_a_b", "boot_partition"}:
        fail("Unexpected normal configuration")

    if set(trial) != {"boot_partition"}:
        fail("Unexpected trial configuration")

    if normal["tryboot_a_b"] != "1":
        fail("tryboot_a_b disabled")

    if normal["boot_partition"] not in ("2", "3"):
        fail("Invalid normal boot partition")

    if trial["boot_partition"] not in ("2", "3"):
        fail("Invalid trial boot partition")

    if normal["boot_partition"] == trial["boot_partition"]:
        fail("Normal and trial partitions are identical")

    return normal["boot_partition"], trial["boot_partition"]


def render(normal, trial):
    return (
        "[all]\n"
        "tryboot_a_b=1\n"
        f"boot_partition={normal}\n\n"
        "[tryboot]\n"
        f"boot_partition={trial}\n"
    ).encode("ascii")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-root", required=True)
    parser.add_argument("--candidate", choices=("system0", "system1"),
                        required=True)
    args = parser.parse_args()

    root = Path(args.lab_root).absolute()

    marker = root / ".secureedge-offline-lab"
    if not marker.is_file() or marker.is_symlink():
        fail("Offline laboratory marker missing")

    if root.is_symlink():
        fail("Laboratory root cannot be a symlink")

    if root.resolve() in (Path("/"), Path("/bootctl"), Path("/data")):
        fail("Unsafe laboratory root")

    source = root / "autoboot.txt"
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)

    if output_dir.is_symlink():
        fail("Output directory cannot be a symlink")

    output = output_dir / "autoboot.txt"
    journal = output_dir / "confirmation.json"
    lock = output_dir / ".confirmation.lock"

    for path in (source, output, journal, lock):
        if path.is_symlink():
            fail(f"Symlink rejected: {path}")

    if not source.is_file() or not stat.S_ISREG(source.stat().st_mode):
        fail("Source autoboot.txt missing")

    if journal.exists() or output.exists():
        fail("Existing transaction: use a fresh laboratory")

    target = "2" if args.candidate == "system0" else "3"

    with open(lock, "a+b") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)

        original = source.read_bytes()
        primary, trial = parse_autoboot(original)

        if trial != target:
            fail("Candidate is not the configured trial partition")

        new_config = render(target, primary)
        if parse_autoboot(new_config) != (target, primary):
            fail("Rendered configuration failed validation")

        txn = {
            "schema": 1,
            "mode": "offline-lab",
            "candidate": args.candidate,
            "previous_primary_partition": primary,
            "new_primary_partition": target,
            "source_sha256": hashlib.sha256(original).hexdigest(),
            "new_sha256": hashlib.sha256(new_config).hexdigest(),
            "status": "prepared",
        }

        durable_write(journal, (json.dumps(txn, indent=2) + "\n").encode())
        durable_write(output, new_config)

        if hashlib.sha256(output.read_bytes()).hexdigest() != txn["new_sha256"]:
            fail("Readback verification failed")

        txn["status"] = "committed"
        durable_write(journal, (json.dumps(txn, indent=2) + "\n").encode())

        print("BOOTCTL_LAB_CONFIRM=PASS")
        print(f"OLD_PRIMARY_PARTITION={primary}")
        print(f"NEW_PRIMARY_PARTITION={target}")
        print("JOURNAL=committed")
        print("REAL_BOOTCTL_WRITES=NO")


if __name__ == "__main__":
    main()
