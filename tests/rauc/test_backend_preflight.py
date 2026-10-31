import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BACKEND = (
    ROOT
    / "meta-secureedge-platform"
    / "recipes-bsp"
    / "secureedge-rauc-backend"
    / "files"
    / "secureedge-rauc-backend"
)


class BackendPreflightTests(unittest.TestCase):

    def test_backend_exists(self):
        self.assertTrue(BACKEND.is_file())

    def test_backend_shell_syntax(self):
        result = subprocess.run(
            ["sh", "-n", str(BACKEND)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_backend_declares_rauc_operations(self):
        source = BACKEND.read_text(encoding="utf-8")

        for operation in (
            "get-primary",
            "set-primary",
            "get-state",
            "set-state",
        ):
            with self.subTest(operation=operation):
                self.assertIn(operation, source)


if __name__ == "__main__":
    unittest.main()
