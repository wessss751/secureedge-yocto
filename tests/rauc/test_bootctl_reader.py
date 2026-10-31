import tempfile
import unittest
from pathlib import Path

from bootctl_reader import BootctlError, read_bootctl


class BootctlReaderTests(unittest.TestCase):

    def parse(self, contents):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "autoboot.txt"
            path.write_text(contents, encoding="utf-8")
            return read_bootctl(path)

    def test_a_primary(self):
        result = self.parse(
            "[all]\n"
            "tryboot_a_b=1\n"
            "boot_partition=2\n"
            "[tryboot]\n"
            "boot_partition=3\n"
        )
        self.assertEqual(result["primary"], "system0")

    def test_b_primary(self):
        result = self.parse(
            "[all]\n"
            "tryboot_a_b=1\n"
            "boot_partition=3\n"
            "[tryboot]\n"
            "boot_partition=2\n"
        )
        self.assertEqual(result["primary"], "system1")

    def test_missing_tryboot(self):
        with self.assertRaises(BootctlError):
            self.parse("[all]\ntryboot_a_b=1\nboot_partition=2\n")

    def test_same_partition_rejected(self):
        with self.assertRaises(BootctlError):
            self.parse(
                "[all]\ntryboot_a_b=1\nboot_partition=2\n"
                "[tryboot]\nboot_partition=2\n"
            )

    def test_invalid_partition(self):
        with self.assertRaises(BootctlError):
            self.parse(
                "[all]\ntryboot_a_b=1\nboot_partition=99\n"
                "[tryboot]\nboot_partition=3\n"
            )

    def test_duplicate_key(self):
        with self.assertRaises(BootctlError):
            self.parse(
                "[all]\ntryboot_a_b=1\n"
                "boot_partition=2\nboot_partition=3\n"
                "[tryboot]\nboot_partition=3\n"
            )

    def test_missing_file(self):
        with self.assertRaises(BootctlError):
            read_bootctl("/nonexistent/secureedge/autoboot.txt")

    def test_unexpected_key(self):
        with self.assertRaises(BootctlError):
            self.parse(
                "[all]\ntryboot_a_b=1\nboot_partition=2\n"
                "dangerous_setting=1\n"
                "[tryboot]\nboot_partition=3\n"
            )

    def test_disabled_tryboot(self):
        with self.assertRaises(BootctlError):
            self.parse(
                "[all]\ntryboot_a_b=0\nboot_partition=2\n"
                "[tryboot]\nboot_partition=3\n"
            )

    def test_non_numeric_value(self):
        with self.assertRaises(BootctlError):
            self.parse(
                "[all]\ntryboot_a_b=1\nboot_partition=abc\n"
                "[tryboot]\nboot_partition=3\n"
            )


if __name__ == "__main__":
    unittest.main()
