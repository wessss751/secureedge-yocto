#!/usr/bin/env python3
"""Offline state-machine tests using self-created temporary fixtures."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).with_name("secureedge-ota-transaction-lab.py").resolve()


class TransactionLabTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="secureedge-ota-test-", dir="/tmp")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / ".secureedge-offline-lab").touch()

    def run_action(self, action, primary=None, candidate=None):
        command = [sys.executable, "-B", str(TOOL), "--lab-root", str(self.root), "--action", action]
        if primary is not None:
            command += ["--primary", primary]
        if candidate is not None:
            command += ["--candidate", candidate]
        return subprocess.run(
            command, cwd=self.root,
            env={"PATH": os.defpath, "HOME": str(self.root), "LC_ALL": "C"},
            capture_output=True, text=True, timeout=10, check=False,
        )

    def read_state(self):
        return json.loads((self.root / "transaction.json").read_text())["state"]

    def initialize(self, primary="system0", candidate="system1"):
        result = self.run_action("init", primary, candidate)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read_state(), "STABLE")

    def advance(self, action, expected):
        result = self.run_action(action)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read_state(), expected)
        self.assertIn("REAL_BOOTCTL_WRITES=NO", result.stdout.splitlines())
        self.assertIn("REAL_REBOOT=NO", result.stdout.splitlines())

    def reject(self, action, reason, primary=None, candidate=None):
        before = (self.root / "transaction.json").read_bytes()
        result = self.run_action(action, primary, candidate)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, f"BLOCKED: {reason}\n")
        self.assertEqual(result.stdout, "")
        self.assertEqual((self.root / "transaction.json").read_bytes(), before)

    def test_nominal_a_to_b(self):
        self.initialize()
        for action, expected in (("installed", "INSTALLED"), ("arm-trial", "TRIAL_ARMED"),
                                 ("verified-boot", "TRIAL_VERIFIED"), ("commit", "COMMITTED")):
            self.advance(action, expected)

    def test_nominal_b_to_a(self):
        self.initialize("system1", "system0")
        for action, expected in (("installed", "INSTALLED"), ("arm-trial", "TRIAL_ARMED"),
                                 ("verified-boot", "TRIAL_VERIFIED"), ("commit", "COMMITTED")):
            self.advance(action, expected)

    def test_premature_confirmation(self):
        self.initialize()
        self.reject("commit", "Forbidden transition: STABLE -> commit")

    def test_abort_before_trial(self):
        self.initialize()
        self.advance("installed", "INSTALLED")
        self.advance("abort", "ABORTED")
        self.reject("commit", "Forbidden transition: ABORTED -> commit")

    def test_abort_after_trial_preparation(self):
        self.initialize()
        self.advance("installed", "INSTALLED")
        self.advance("arm-trial", "TRIAL_ARMED")
        self.advance("abort", "ABORTED")

    def test_duplicate_initialization(self):
        self.initialize()
        self.reject("init", "Existing transaction", "system0", "system1")


if __name__ == "__main__":
    unittest.main()
