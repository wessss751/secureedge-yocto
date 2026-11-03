#!/usr/bin/env python3
"""SecureEdge signed RAUC target audit.

Read-only. No tryboot authorization, no BOOTCTL writes.
Requires an existing successful RAUC installation transaction.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RECORD = Path("/data/secureedge-rauc/last-install.json")
KEYRING = Path("/etc/rauc/ca.cert.pem")

PARTITIONS = {
    "rootfs": Path("/dev/mmcblk0p6"),
    "boot": Path("/dev/mmcblk0p3"),
}


def fail(message):
    raise SystemExit(f"AUDIT=BLOCKED: {message}")


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while True:
            chunk = source.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True)
    args = parser.parse_args()

    if os.geteuid() != 0:
        fail("Root required")

    bundle = Path(args.bundle)

    if not bundle.is_absolute() or bundle.is_symlink():
        fail("Invalid bundle path")

    if not bundle.is_file():
        fail("Bundle unavailable")

    if RECORD.is_symlink() or not RECORD.is_file():
        fail("Transaction unavailable")

    record = json.loads(RECORD.read_text())

    if record.get("schema") != 2:
        fail("Unexpected transaction schema")

    if record.get("state") != "installed_unverified":
        fail("Transaction not ready for verification")

    if record.get("rauc_exit_code") != 0:
        fail("RAUC installation not successful")

    if record.get("install_completed") is not True:
        fail("Missing installation completion")

    if record.get("tryboot_authorized") is not False:
        fail("Unexpected boot authorization")

    if record.get("target_verified") is not False:
        fail("Unexpected target state")

    expected_bundle_hash = record.get("bundle_sha256", "")

    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_bundle_hash):
        fail("Invalid recorded bundle hash")

    if sha256_file(bundle) != expected_bundle_hash.lower():
        fail("Bundle differs from installation record")

    cmdline = Path("/proc/cmdline").read_text().split()

    if (
        "root=/dev/mmcblk0p5" not in cmdline
        or "rauc.slot=system0" not in cmdline
    ):
        fail("Not running the expected primary system A")

    if not KEYRING.is_file():
        fail("Trusted RAUC keyring missing")

    result = subprocess.run(
        [
            "/usr/bin/rauc",
            "info",
            f"--keyring={KEYRING}",
            "--output-format=json-2",
            str(bundle),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    if result.returncode != 0:
        fail("RAUC signature or bundle inspection failed")

    try:
        signed_info = json.loads(result.stdout)
    except json.JSONDecodeError:
        fail("Invalid authenticated RAUC metadata")

    print("BUNDLE_SIGNATURE=VERIFIED")
    print("BUNDLE_TRANSACTION_HASH=MATCH")
    print("SIGNED_METADATA=AVAILABLE")
    print("SIGNED_METADATA_TOP_LEVEL=", sorted(signed_info))
    print("TARGET_IMAGES_VERIFIED=NO")
    print("TRYBOOT_AUTHORIZED=NO")
    print("BOOTCTL_MODIFIED=NO")


if __name__ == "__main__":
    main()
