#!/usr/bin/env python3
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = (Path(__file__).resolve().parents[2] / "meta-secureedge-platform"
        / "recipes-core/secureedge-rauc-boot-proof/files/secureedge-rauc-boot-proof")


class BootProofTests(unittest.TestCase):
    def check_case(self, primary, trial, slot, fw_boot, tryboot,
                   pending=None, expected="NORMAL_PRIMARY"):
        with tempfile.TemporaryDirectory(prefix="secureedge-proof-", dir="/tmp") as directory:
            root = Path(directory)
            (root / ".secureedge-offline-lab").touch()
            (root / "firmware").mkdir()
            (root / "autoboot.txt").write_text(
                "[all]\ntryboot_a_b=1\n"
                f"boot_partition={primary}\n\n[tryboot]\nboot_partition={trial}\n"
            )
            rootfs = "/dev/mmcblk0p5" if slot == "system0" else "/dev/mmcblk0p6"
            (root / "cmdline").write_text(f"root={rootfs} rootwait rauc.slot={slot}\n")
            for key, value in (("partition", fw_boot), ("tryboot", tryboot)):
                (root / "firmware" / key).write_bytes(struct.pack(">I", value))
            if pending is not None:
                (root / "pending-slot").write_text(pending + "\n")
            before = {str(p.relative_to(root)): p.read_bytes()
                      for p in root.rglob("*") if p.is_file()}
            result = subprocess.run(
                [sys.executable, "-B", str(TOOL), "--fixture", str(root)],
                cwd=root, env={"PATH": os.defpath, "HOME": directory, "LC_ALL": "C"},
                text=True, capture_output=True, timeout=10, check=False,
            )
            self.assertEqual(result.returncode, 2 if expected == "BLOCKED" else 0, result.stderr)
            self.assertEqual(result.stderr, "")
            data = json.loads(result.stdout)
            self.assertEqual(data["result"], expected)
            self.assertIs(data["writes"], False)
            after = {str(p.relative_to(root)): p.read_bytes()
                     for p in root.rglob("*") if p.is_file()}
            self.assertEqual(after, before)

    def test_normal_a(self):
        self.check_case(2, 3, "system0", 2, 0)

    def test_trial_b(self):
        self.check_case(2, 3, "system1", 3, 1, "system1", "TRIAL_CANDIDATE")

    def test_normal_b(self):
        self.check_case(3, 2, "system1", 3, 0)

    def test_wrong_firmware_partition(self):
        self.check_case(2, 3, "system1", 2, 1, "system1", "BLOCKED")

    def test_trial_without_pending(self):
        self.check_case(2, 3, "system1", 3, 1, None, "BLOCKED")


if __name__ == "__main__":
    unittest.main()
