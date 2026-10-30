
import os
import subprocess
import tempfile
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


class BackendSetPrimaryTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.directory = Path(self.temp.name)
        self.states = self.directory / "bootstate"
        self.states.mkdir()

        (self.states / "system0").write_text("good\n")
        (self.states / "system1").write_text("bad\n")

        self.autoboot = self.directory / "autoboot.txt"
        self.cmdline = self.directory / "cmdline.txt"

        self.configure_boot(2, 3, "system0", 5)

        self.environment = os.environ.copy()
        self.environment.update({
            "SECUREEDGE_TEST_MODE": "1",
            "SECUREEDGE_BOOTCTL_DIR": str(self.directory),
            "SECUREEDGE_STATE_DIR": str(self.states),
            "SECUREEDGE_CMDLINE_FILE": str(self.cmdline),
        })

    def configure_boot(self, normal, trial, running, root):
        self.autoboot.write_text(
            "[all]\n"
            "tryboot_a_b=1\n"
            f"boot_partition={normal}\n"
            "[tryboot]\n"
            f"boot_partition={trial}\n"
        )

        self.cmdline.write_text(
            f"root=/dev/mmcblk0p{root} "
            f"rauc.slot={running}\n"
        )

    def backend(self, *args, simulation=True):
        env = self.environment.copy()
        env["SECUREEDGE_TEST_MODE"] = (
            "1" if simulation else "0"
        )

        return subprocess.run(
            ["/bin/sh", str(BACKEND), *args],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_prepare_a_to_b(self):
        before = self.autoboot.read_bytes()

        result = self.backend("set-primary", "system1")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.states / "pending-slot").read_text().strip(),
            "system1",
        )
        self.assertEqual(self.autoboot.read_bytes(), before)

        primary = self.backend("get-primary")
        self.assertEqual(primary.stdout.strip(), "system0")

    def test_prepare_b_to_a(self):
        self.configure_boot(3, 2, "system1", 6)

        (self.states / "system0").write_text("bad\n")
        (self.states / "system1").write_text("good\n")

        before = self.autoboot.read_bytes()

        result = self.backend("set-primary", "system0")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.states / "pending-slot").read_text().strip(),
            "system0",
        )
        self.assertEqual(self.autoboot.read_bytes(), before)

        primary = self.backend("get-primary")
        self.assertEqual(primary.stdout.strip(), "system1")

    def test_reject_active_slot(self):
        result = self.backend("set-primary", "system0")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.states / "pending-slot").exists())

    def test_reject_unknown_slot(self):
        result = self.backend("set-primary", "system9")
        self.assertNotEqual(result.returncode, 0)

    def test_reject_unhealthy_normal_slot(self):
        (self.states / "system0").write_text("bad\n")
        result = self.backend("set-primary", "system1")
        self.assertNotEqual(result.returncode, 0)

    def test_reject_wrong_running_slot(self):
        self.configure_boot(2, 3, "system1", 6)
        result = self.backend("set-primary", "system1")
        self.assertNotEqual(result.returncode, 0)

    def test_reject_outside_simulation(self):
        result = self.backend(
            "set-primary",
            "system1",
            simulation=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.states / "pending-slot").exists())


if __name__ == "__main__":
    unittest.main()
