
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SIM = (
    PROJECT
    / "meta-secureedge-platform"
    / "recipes-bsp"
    / "secureedge-rauc-commit"
    / "files"
    / "secureedge-bootctl-transaction-sim"
)


class BootctlTransactionTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.lab = Path(self.temp.name) / "trial"

        result = self.execute("init")
        self.assertEqual(result.returncode, 0, result.stdout)

    def execute(self, action, *extra):
        return subprocess.run(
            [
                sys.executable,
                str(SIM),
                action,
                "--sandbox",
                str(self.lab),
                *extra,
            ],
            capture_output=True,
            text=True,
        )

    def boot_content(self):
        return (self.lab / "BOOTCTL/autoboot.txt").read_text()

    def journal_state(self):
        import json
        return json.loads(
            (self.lab / "DATA/transaction.json").read_text()
        )["state"]

    def test_normal_commit(self):
        result = self.execute("promote")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("boot_partition=3", self.boot_content())
        self.assertEqual(self.journal_state(), "committed")

    def test_fault_after_prepared(self):
        self.assertNotEqual(
            self.execute("promote", "--fault", "after-prepared").returncode,
            0,
        )
        self.assertEqual(self.execute("recover").returncode, 0)
        self.assertEqual(self.journal_state(), "recovered")
        self.assertIn("boot_partition=2", self.boot_content())

    def test_fault_before_replace(self):
        self.assertNotEqual(
            self.execute("promote", "--fault", "before-replace").returncode,
            0,
        )
        self.assertEqual(self.execute("recover").returncode, 0)
        self.assertEqual(self.journal_state(), "recovered")

    def test_fault_after_replace(self):
        self.assertNotEqual(
            self.execute("promote", "--fault", "after-replace").returncode,
            0,
        )
        self.assertEqual(self.execute("recover").returncode, 0)
        self.assertEqual(self.journal_state(), "recovered")
        self.assertIn("boot_partition=2", self.boot_content())

    def test_double_commit_rejected(self):
        self.assertEqual(self.execute("promote").returncode, 0)
        self.assertNotEqual(self.execute("promote").returncode, 0)

    def test_committed_state_remains_committed(self):
        self.assertEqual(self.execute("promote").returncode, 0)
        self.assertEqual(self.execute("recover").returncode, 0)
        self.assertEqual(self.journal_state(), "committed")

    def test_corruption_requires_manual_recovery(self):
        self.execute("promote", "--fault", "after-replace")
        (self.lab / "BOOTCTL/autoboot.txt").write_text("CORRUPTED")
        result = self.execute("recover")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(
            self.journal_state(),
            "manual_recovery_required",
        )

    def test_cannot_use_arbitrary_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable, str(SIM), "promote",
                    "--sandbox", directory,
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
