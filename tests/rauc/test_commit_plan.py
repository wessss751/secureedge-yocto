
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
PLAN = (
    PROJECT
    / "meta-secureedge-platform"
    / "recipes-bsp"
    / "secureedge-rauc-commit"
    / "files"
    / "secureedge-rauc-commit-plan"
)


class CommitPlanTests(unittest.TestCase):
    def run_plan(self, **overrides):
        values = {
            "current": "system1",
            "primary": "system0",
            "candidate": "system1",
            "tryboot-target": "system1",
            "tryboot": "1",
            "firmware-partition": "3",
            "health-ok": "1",
        }
        values.update(overrides)
        command = [sys.executable, str(PLAN)]
        for key, value in values.items():
            command += [f"--{key}", value]
        return subprocess.run(command, capture_output=True, text=True)

    def test_valid_a_to_b(self):
        result = self.run_plan()
        self.assertEqual(result.returncode, 0)
        self.assertIn("normal_boot_partition=3", result.stdout)
        self.assertIn("NO_CHANGES_WRITTEN", result.stdout)

    def test_valid_b_to_a(self):
        result = self.run_plan(
            current="system0",
            primary="system1",
            candidate="system0",
            **{"tryboot-target": "system0",
               "firmware-partition": "2"}
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("normal_boot_partition=2", result.stdout)

    def test_failed_health(self):
        self.assertNotEqual(
            self.run_plan(**{"health-ok": "0"}).returncode, 0
        )

    def test_no_tryboot(self):
        self.assertNotEqual(
            self.run_plan(tryboot="0").returncode, 0
        )

    def test_wrong_firmware_partition(self):
        self.assertNotEqual(
            self.run_plan(**{"firmware-partition": "2"}).returncode, 0
        )

    def test_wrong_tryboot_target(self):
        self.assertNotEqual(
            self.run_plan(**{"tryboot-target": "system0"}).returncode, 0
        )

    def test_wrong_running_slot(self):
        self.assertNotEqual(
            self.run_plan(current="system0").returncode, 0
        )


if __name__ == "__main__":
    unittest.main()
