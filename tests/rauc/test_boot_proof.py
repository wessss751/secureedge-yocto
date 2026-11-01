#!/usr/bin/env python3
import json
import struct
import subprocess
import tempfile
from pathlib import Path

TOOL = Path(
    "meta-secureedge-platform/recipes-core/"
    "secureedge-rauc-boot-proof/files/"
    "secureedge-rauc-boot-proof"
).resolve()


def case(name, primary, trial, slot, fw_boot, tryboot,
         pending=None, expected="NORMAL_PRIMARY"):

    with tempfile.TemporaryDirectory(
        prefix="secureedge-proof-", dir="/tmp"
    ) as directory:

        root = Path(directory)
        (root / ".secureedge-offline-lab").touch()
        (root / "firmware").mkdir()

        (root / "autoboot.txt").write_text(
            "[all]\n"
            "tryboot_a_b=1\n"
            f"boot_partition={primary}\n\n"
            "[tryboot]\n"
            f"boot_partition={trial}\n"
        )

        rootfs = (
            "/dev/mmcblk0p5" if slot == "system0"
            else "/dev/mmcblk0p6"
        )

        (root / "cmdline").write_text(
            f"root={rootfs} rootwait rauc.slot={slot}\n"
        )

        for key, value in (
            ("partition", fw_boot),
            ("tryboot", tryboot),
        ):
            (root / "firmware" / key).write_bytes(
                struct.pack(">I", value)
            )

        if pending is not None:
            (root / "pending-slot").write_text(pending + "\n")

        result = subprocess.run(
            ["python3", str(TOOL), "--fixture", str(root)],
            text=True,
            capture_output=True,
        )

        data = json.loads(result.stdout)

        assert data["result"] == expected, (
            name, data, result.stderr
        )

        assert result.returncode == (
            2 if expected == "BLOCKED" else 0
        )

        print(f"PASS: {name} -> {expected}")


case("A normal", 2, 3, "system0", 2, 0)
case("B trial", 2, 3, "system1", 3, 1, "system1",
     "TRIAL_CANDIDATE")
case("B confirmed", 3, 2, "system1", 3, 0)
case("Wrong firmware partition", 2, 3, "system1", 2, 1,
     "system1", "BLOCKED")
case("Trial without pending", 2, 3, "system1", 3, 1,
     None, "BLOCKED")

print("BOOT_PROOF_TESTS=PASS")
print("HARDWARE_WRITES=NO")
