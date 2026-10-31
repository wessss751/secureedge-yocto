import subprocess
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]

BACKEND = (
    PROJECT
    / "meta-secureedge-platform"
    / "recipes-bsp"
    / "secureedge-rauc-backend"
    / "files"
    / "secureedge-rauc-backend"
)


class CustomBackendSafetyTests(unittest.TestCase):

    def invoke(self, *args):
        return subprocess.run(
            ["/bin/sh", str(BACKEND), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )

    def test_unknown_command_is_rejected(self):
        result = self.invoke("unknown-command")
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_primary_is_rejected(self):
        result = self.invoke(
            "set-primary",
            "invalid-slot",
        )
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_state_is_rejected(self):
        result = self.invoke(
            "set-state",
            "system1",
            "invalid-state",
        )
        self.assertNotEqual(result.returncode, 0)

    def test_missing_slot_is_rejected(self):
        result = self.invoke("set-primary")
        self.assertNotEqual(result.returncode, 0)

    def test_extra_argument_is_rejected(self):
        result = self.invoke(
            "set-primary",
            "invalid-slot",
            "extra",
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
