#!/usr/bin/env python3
"""SecureEdge A/B confirmation integration simulation.

Runs only on a self-created temporary filesystem.
Never writes to physical BOOTCTL or device partitions.
"""

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BACKEND = (
    ROOT / "meta-secureedge-platform"
    / "recipes-bsp/secureedge-rauc-backend/files"
    / "secureedge-rauc-backend"
)

RENDERER = ROOT / "scripts/rauc/secureedge-bootctl-render.py"


def run(*args, env=None):
    result = subprocess.run(
        list(args),
        check=True,
        text=True,
        capture_output=True,
        timeout=15,
        env=env,
    )
    return result.stdout.strip()


def main():
    with tempfile.TemporaryDirectory(prefix="secureedge-ab-") as tmp:
        base = Path(tmp)
        bootctl = base / "bootctl"
        state = base / "state"
        firmware = base / "firmware"

        for directory in (bootctl, state, firmware):
            directory.mkdir()

        autoboot = bootctl / "autoboot.txt"

        autoboot.write_text(
            "[all]\n"
            "tryboot_a_b=1\n"
            "boot_partition=2\n\n"
            "[tryboot]\n"
            "boot_partition=3\n",
            encoding="ascii",
        )

        (state / "system0").write_text("good\n")
        (state / "system1").write_text("bad\n")

        cmdline = base / "cmdline"
        cmdline.write_text(
            "root=/dev/mmcblk0p5 rauc.slot=system0\n"
        )

        env = os.environ.copy()
        env.update({
            "SECUREEDGE_TEST_MODE": "1",
            "SECUREEDGE_BOOTCTL_DIR": str(bootctl),
            "SECUREEDGE_STATE_DIR": str(state),
            "SECUREEDGE_CMDLINE_FILE": str(cmdline),
            "SECUREEDGE_FIRMWARE_DIR": str(firmware),
        })

        print("=== 1. NORMAL BOOT A ===")
        assert run("sh", str(BACKEND), "get-primary", env=env) == "system0"

        print("=== 2. PREPARE B ===")
        run("sh", str(BACKEND), "set-primary", "system1", env=env)

        assert (state / "pending-slot").read_text().strip() == "system1"

        print("=== 3. SIMULATE FIRMWARE TRYBOOT B ===")
        cmdline.write_text(
            "root=/dev/mmcblk0p6 rauc.slot=system1\n"
        )

        (firmware / "tryboot").write_bytes((1).to_bytes(4, "big"))
        (firmware / "partition").write_bytes((3).to_bytes(4, "big"))

        verification = run(
            "sh", str(BACKEND), "verify-tryboot", env=env
        )

        assert verification == "verified-tryboot=system1"

        print("=== 4. SIMULATED HEALTH GATE ===")
        simulated_health_ok = True
        assert simulated_health_ok

        print("=== 5. RENDER CONFIRMATION ===")
        result = run(
            "python3",
            str(RENDERER),
            str(autoboot),
            "system0",
            "system1",
        )

        assert "boot_partition=3" in result
        assert result == (
            "[all]\n"
            "tryboot_a_b=1\n"
            "boot_partition=3\n\n"
            "[tryboot]\n"
            "boot_partition=2"
        )

        assert run("sh", str(BACKEND), "get-primary", env=env) == "system0"

        print(result)
        print("PASS: A/B CONFIRMATION SIMULATION")
        print("NO PHYSICAL BOOTCTL MODIFIED")


if __name__ == "__main__":
    main()
