#!/usr/bin/env python3
"""SecureEdge offline OTA readiness audit. No device writes."""

import argparse
import gzip
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run(args):
    try:
        return subprocess.run(
            args,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        return subprocess.CompletedProcess(args, 127, "", str(exc))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--backup-dir",
        default="/mnt/secureedge-storage/rauc-ab-tests/"
                "backup-before-real-ota",
    )
    parser.add_argument(
        "--bundle-input",
        default="/mnt/secureedge-storage/rauc-ab-tests/"
                "bundles/phase10-complete",
    )
    parser.add_argument(
        "--wic",
        default="/mnt/secureedge-storage/rauc-ab-tests/"
                "bundles/phase10-disk.wic",
    )
    args = parser.parse_args()

    project = Path(args.project).resolve()
    output = Path(args.output).resolve()
    backup_dir = Path(args.backup_dir)
    bundle_input = Path(args.bundle_input)
    wic = Path(args.wic)

    results = []

    def record(name, state, detail):
        results.append({
            "check": name,
            "state": state,
            "detail": detail,
        })
        print(f"{state}: {name} — {detail}")

    backup = backup_dir / "secureedge-current-pre-ota.img.gz"
    checksum = backup_dir / (
        "secureedge-current-pre-ota.img.gz.sha256"
    )

    if backup.is_file() and backup.stat().st_size:
        record("backup_exists", "PASS", str(backup))
    else:
        record("backup_exists", "FAIL", "Backup missing or empty")

    if backup.is_file() and checksum.is_file():
        expected = checksum.read_text().split()
        if expected and re.fullmatch(r"[0-9a-fA-F]{64}", expected[0]):
            actual = sha256(backup)
            if actual.lower() == expected[0].lower():
                record("backup_sha256", "PASS", "SHA-256 matches")
            else:
                record("backup_sha256", "FAIL", "SHA-256 mismatch")
        else:
            record("backup_sha256", "FAIL", "Invalid checksum file")
    else:
        record("backup_sha256", "FAIL", "Checksum evidence missing")

    if backup.is_file():
        try:
            with gzip.open(backup, "rb") as stream:
                while stream.read(4 * 1024 * 1024):
                    pass
            record("backup_gzip", "PASS", "Gzip stream readable")
        except (OSError, EOFError) as exc:
            record("backup_gzip", "FAIL", str(exc))

    rootfs = bundle_input / "rootfs.ext4"
    boot = bundle_input / "boot.vfat"

    for name, path in [
        ("rootfs_image", rootfs),
        ("boot_image", boot),
    ]:
        if path.is_file() and path.stat().st_size:
            record(name, "PASS", f"{path.stat().st_size} bytes")
        else:
            record(name, "FAIL", f"Missing or empty: {path}")

    for name, path, wanted in [
        ("rootfs_format", rootfs, "ext4"),
        ("boot_format", boot, "vfat"),
    ]:
        if not path.is_file():
            record(name, "FAIL", "Image missing")
            continue

        probe = run(["blkid", "-p", "-o", "value", "-s", "TYPE", str(path)])
        fs_type = probe.stdout.strip()

        if probe.returncode == 0 and fs_type == wanted:
            record(name, "PASS", fs_type)
        else:
            record(name, "FAIL", f"Detected: {fs_type or 'unknown'}")

    if boot.is_file():
        result = run(["mtype", "-i", str(boot), "::cmdline.txt"])
        cmdline = result.stdout.strip()

        expected_tokens = {
            "root=/dev/mmcblk0p6",
            "rauc.slot=system1",
        }

        if result.returncode == 0 and expected_tokens.issubset(
            set(cmdline.split())
        ):
            record("boot_b_cmdline", "PASS", cmdline)
        else:
            record("boot_b_cmdline", "FAIL", "Slot B mismatch")

        listing = run(["mdir", "-i", str(boot), "::"])
        if listing.returncode == 0 and all(
            token in listing.stdout.lower()
            for token in ("kernel8", "config", "cmdline")
        ):
            record("boot_b_files", "PASS", "Essential files found")
        else:
            record("boot_b_files", "FAIL", "Boot file inventory incomplete")

    if wic.is_file():
        result = run(["sfdisk", "--json", str(wic)])
        if result.returncode == 0:
            try:
                table = json.loads(result.stdout)["partitiontable"]
                parts = table["partitions"]
                sizes = [p["size"] for p in parts]
                expected = [
                    131072,
                    393216,
                    393216,
                    4210690,
                    1048576,
                    1048576,
                    2097152,
                ]
                if sizes == expected:
                    record(
                        "wic_layout",
                        "PASS",
                        "BOOTCTL / A / B / extended / ROOTFS_A / "
                        "ROOTFS_B / DATA",
                    )
                else:
                    record(
                        "wic_layout",
                        "FAIL",
                        f"Unexpected partition sectors: {sizes}",
                    )
            except (KeyError, ValueError, TypeError) as exc:
                record("wic_layout", "FAIL", str(exc))
        else:
            record("wic_layout", "FAIL", result.stderr.strip())
    else:
        record("wic_layout", "FAIL", "WIC missing")

    backend = (
        project
        / "meta-secureedge-platform/recipes-bsp/"
        "secureedge-rauc-backend/files/secureedge-rauc-backend"
    )
    trial = (
        project
        / "meta-secureedge-platform/recipes-core/"
        "secureedge-rauc-trial/files/secureedge-rauc-trial"
    )
    health = project / "scripts/rauc/secureedge-health-gate.sh"
    confirm = project / "scripts/rauc/secureedge-bootctl-confirm-lab.py"
    recover = project / "scripts/rauc/secureedge-bootctl-recover-lab.py"

    for name, path in [
        ("backend_syntax", backend),
        ("trial_syntax", trial),
        ("health_syntax", health),
    ]:
        if not path.is_file():
            record(name, "FAIL", "Source missing")
            continue
        result = run(["sh", "-n", str(path)])
        record(
            name,
            "PASS" if result.returncode == 0 else "FAIL",
            "Syntax valid" if result.returncode == 0
            else result.stderr.strip(),
        )

    for name, path in [
        ("confirm_lab_source", confirm),
        ("recovery_lab_source", recover),
    ]:
        if path.is_file():
            record(name, "PASS", "Laboratory source present")
        else:
            record(name, "FAIL", "Laboratory source missing")

    blockers = [
        "RAUC set-primary hardware contract not demonstrated",
        "Authenticated completed-install transaction not demonstrated",
        "Power-loss-qualified FAT BOOTCTL update not demonstrated",
        "Production trial reboot controller not demonstrated",
        "Candidate device provisioning not verified",
        "Real A-to-B OTA and normal B reboot not demonstrated",
        "Real failed-B rollback not demonstrated",
    ]

    report = {
        "schema": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "offline-readiness",
        "hardware_status": "NO-GO",
        "results": results,
        "hardware_blockers": blockers,
        "no_device_writes": True,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")

    failed = sum(r["state"] == "FAIL" for r in results)
    passed = sum(r["state"] == "PASS" for r in results)

    print()
    print(f"OFFLINE_PASS={passed}")
    print(f"OFFLINE_FAIL={failed}")
    print("HARDWARE_OTA=NO-GO")
    print("DEVICE_WRITES=NO")
    print(f"REPORT={output}")

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(audit())
