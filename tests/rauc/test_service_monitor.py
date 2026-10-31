
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]

MONITOR = (
    PROJECT
    / "meta-secureedge-platform"
    / "recipes-core"
    / "secureedge-service-monitor"
    / "files"
    / "secureedge-service-monitor"
)


class ServiceMonitorTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

        root = Path(self.tmp.name)
        self.units = root / "units"
        self.systemctl = root / "systemctl"

        self.systemctl.write_text(
            "#!/bin/sh\n"
            "[ \"$1\" = is-active ] || exit 1\n"
            "[ \"$2\" = --quiet ] || exit 1\n"
            "[ \"$3\" != failed.service ]\n"
        )
        self.systemctl.chmod(0o755)

    def run_monitor(self, content):
        self.units.write_text(content)

        env = os.environ.copy()
        env["SECUREEDGE_SYSTEMCTL"] = str(self.systemctl)
        env["SECUREEDGE_UNITS_FILE"] = str(self.units)

        return subprocess.run(
            ["/bin/sh", str(MONITOR)],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_all_units_active(self):
        result = self.run_monitor(
            "data.mount\nbootctl.mount\nsecureedge-agent.service\n"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("HEALTH_OK", result.stdout)

    def test_failed_service(self):
        result = self.run_monitor("failed.service\n")
        self.assertNotEqual(result.returncode, 0)

    def test_empty_file(self):
        result = self.run_monitor("")
        self.assertNotEqual(result.returncode, 0)

    def test_only_comments(self):
        result = self.run_monitor("# comment\n")
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_unit(self):
        result = self.run_monitor("bad;command.service\n")
        self.assertNotEqual(result.returncode, 0)

    def test_unsupported_unit(self):
        result = self.run_monitor("something.timer\n")
        self.assertNotEqual(result.returncode, 0)

    def test_multiple_valid_units(self):
        result = self.run_monitor(
            "data.mount\nbootctl.mount\n"
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("2 critical units active", result.stdout)


if __name__ == "__main__":
    unittest.main()
