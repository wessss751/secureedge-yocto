#!/usr/bin/env python3
"""Offline BOOTCTL confirmation transaction demonstration."""

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RENDERER = ROOT / "scripts/rauc/secureedge-bootctl-render.py"
FIXTURE = ROOT / "tests/rauc/fixtures/autoboot-a.txt"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    with tempfile.TemporaryDirectory(prefix="secureedge-confirm-") as tmp:
        directory = Path(tmp)
        source = directory / "autoboot.txt"
        candidate = directory / "autoboot.candidate"
        journal = directory / "transaction.log"

        source.write_bytes(FIXTURE.read_bytes())
        old_data = source.read_bytes()

        # Generate a candidate using the existing strict renderer.
        result = subprocess.run(
            [
                "python3", str(RENDERER),
                str(source), "system0", "system1",
            ],
            check=True,
            capture_output=True,
            timeout=10,
        )

        candidate.write_bytes(result.stdout)
        new_data = candidate.read_bytes()

        # In a real implementation these would be persisted
        # with a carefully designed recovery protocol.
        journal.write_text(
            "phase=prepared\n"
            f"old_sha256={sha256(old_data)}\n"
            f"new_sha256={sha256(new_data)}\n"
        )

        # The original remains untouched until the commit point.
        assert source.read_bytes() == old_data

        # Simulated commit on a temporary filesystem.
        os.replace(candidate, source)

        assert source.read_bytes() == new_data

        journal.write_text(
            "phase=committed\n"
            f"new_sha256={sha256(new_data)}\n"
        )

        text = source.read_text(encoding="ascii")

        assert "boot_partition=3" in text
        assert "[tryboot]\nboot_partition=2" in text

        print("PASS: CONFIRMATION TRANSACTION SIMULATION")
        print("OLD_SHA256=", sha256(old_data))
        print("NEW_SHA256=", sha256(new_data))
        print("PRIMARY=system1")
        print("NO PHYSICAL BOOTCTL MODIFIED")


if __name__ == "__main__":
    main()
