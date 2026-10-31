
import json
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


class BootctlFaultTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            prefix="secureedge-faults-"
        )
        self.addCleanup(self.temp.cleanup)

        self.lab = Path(self.temp.name) / "trial"

        result = self.run_action("init")
        self.assertEqual(result.returncode, 0, result.stdout)

        self.boot = self.lab / "BOOTCTL/autoboot.txt"
        self.journal = self.lab / "DATA/transaction.json"

    def run_action(self, action, *extra):
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

    def read_state(self):
        return json.loads(self.journal.read_text())["state"]

    def test_missing_journal_recovery_rejected(self):
        result = self.run_action("recover")
        self.assertNotEqual(result.returncode, 0)

    def test_truncated_journal_rejected(self):
        self.journal.write_text('{"state":')
        result = self.run_action("recover")
        self.assertNotEqual(result.returncode, 0)

    def test_missing_journal_fields_rejected(self):
        self.journal.write_text('{"state":"prepared"}')
        result = self.run_action("recover")
        self.assertNotEqual(result.returncode, 0)

    def test_modified_journal_hash_rejected(self):
        self.run_action(
            "promote", "--fault", "after-prepared"
        )
        record = json.loads(self.journal.read_text())
        record["old_sha256"] = "0" * 64
        self.journal.write_text(json.dumps(record))

        result = self.run_action("recover")
        self.assertNotEqual(result.returncode, 0)

    def test_missing_boot_file_rejected(self):
        self.boot.unlink()
        result = self.run_action("promote")
        self.assertNotEqual(result.returncode, 0)

    def test_symlink_boot_file_rejected(self):
        original = self.boot.read_text()
        backup = self.lab / "BOOTCTL/backup.txt"
        backup.write_text(original)

        self.boot.unlink()
        self.boot.symlink_to(backup)

        result = self.run_action("promote")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(backup.read_text(), original)

    def test_symlink_journal_rejected(self):
        target = self.lab / "DATA/external.txt"
        target.write_text("DO_NOT_MODIFY")
        self.journal.symlink_to(target)

        result = self.run_action("promote")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), "DO_NOT_MODIFY")

    def test_recovery_is_idempotent(self):
        self.run_action(
            "promote", "--fault", "before-replace"
        )

        first = self.run_action("recover")
        second = self.run_action("recover")

        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(self.read_state(), "recovered")
        self.assertIn("boot_partition=2", self.boot.read_text())

    def test_committed_configuration_tamper_rejected(self):
        result = self.run_action("promote")
        self.assertEqual(result.returncode, 0)

        self.boot.write_text("INVALID BOOT CONFIGURATION")

        recovery = self.run_action("recover")
        self.assertNotEqual(recovery.returncode, 0)
        self.assertEqual(
            self.read_state(),
            "manual_recovery_required",
        )

    def test_repeated_promotion_rejected(self):
        first = self.run_action("promote")
        second = self.run_action("promote")

        self.assertEqual(first.returncode, 0)
        self.assertNotEqual(second.returncode, 0)


if __name__ == "__main__":
    unittest.main()
