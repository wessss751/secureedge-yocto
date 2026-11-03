#!/usr/bin/env python3
"""One-time offline migration of SecureEdge identity to DATA.

Must run as root. ROOTFS_A remains read-only.
Does not print TLS secret values.
"""

import os
import re
import shutil
import stat
import sys
from pathlib import Path

ROOT = Path("/mnt/secureedge-rootfs-a")
DATA = Path("/mnt/secureedge-data")
DEST = DATA / "secureedge"

UID = 995
GID = 993

SOURCE_CONFIG = ROOT / "etc/secureedge/agent.conf"
SOURCE_ENV = ROOT / "etc/secureedge/mqtt-tls.env"

TLS_KEYS = (
    "SECUREEDGE_MQTT_CA",
    "SECUREEDGE_MQTT_CERT",
    "SECUREEDGE_MQTT_KEY",
)


def fail(message):
    raise SystemExit(f"BLOCKED: {message}")


def regular(path):
    if path.is_symlink() or not path.is_file():
        fail(f"Invalid source: {path}")


def main():
    if os.geteuid() != 0:
        fail("Root required")

    mounts = Path("/proc/mounts").read_text()

    for mountpoint, required_mode in (
        (str(ROOT), "ro"),
        (str(DATA), "rw"),
    ):
        if not any(
            line.split()[1] == mountpoint
            and line.split()[2] == "ext4"
            and required_mode in line.split()[3].split(",")
            for line in mounts.splitlines()
        ):
            fail(
                f"Expected {required_mode} ext4 mount: {mountpoint}"
            )

    regular(SOURCE_CONFIG)
    regular(SOURCE_ENV)

    env_text = SOURCE_ENV.read_text()
    values = {}

    for line in env_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            fail("Invalid environment line")

        key, value = line.split("=", 1)

        if key in values:
            fail("Duplicate environment variable")

        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            fail("Invalid environment variable")

        value = value.strip().strip('"').strip("'")
        values[key] = value

    if values.get("SECUREEDGE_MQTT_TLS") != "1":
        fail("TLS is not enabled")

    for key in TLS_KEYS:
        if key not in values:
            fail("Missing TLS path variable")

    if DEST.exists() or DEST.is_symlink():
        fail("DATA identity destination already exists")

    files = {}

    for index, key in enumerate(TLS_KEYS):
        source = Path(values[key])

        if not source.is_absolute():
            fail("TLS path must be absolute")

        relative = source.relative_to("/")
        real_source = ROOT / relative

        regular(real_source)

        if not stat.S_ISREG(real_source.lstat().st_mode):
            fail("TLS source is not regular")

        files[key] = (real_source, f"identity/tls-{index}.pem")

    (DEST / "config").mkdir(parents=True, mode=0o750)
    (DEST / "identity").mkdir(mode=0o750)

    os.chown(DEST, 0, GID)
    os.chown(DEST / "config", 0, GID)
    os.chown(DEST / "identity", 0, GID)

    for folder in (DEST, DEST / "config", DEST / "identity"):
        folder.chmod(0o750)

    config_dst = DEST / "config/agent.conf"
    shutil.copyfile(SOURCE_CONFIG, config_dst)
    config_dst.chmod(0o640)
    os.chown(config_dst, 0, GID)

    for key, (source, name) in files.items():
        target = DEST / name
        shutil.copyfile(source, target)
        target.chmod(0o640)
        os.chown(target, 0, GID)
        values[key] = f"/data/secureedge/{name}"

    env_dst = DEST / "identity/mqtt-tls.env"

    with env_dst.open("x", encoding="utf-8") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}\n")

    env_dst.chmod(0o640)
    os.chown(env_dst, 0, GID)

    print("PASS: persistent identity prepared")
    print("ROOTFS_A_MODIFIED=NO")
    print("DATA_IDENTITY_READY=YES")


if __name__ == "__main__":
    main()
