"""Temporary fixtures for the shell backend; never use live device paths."""

import os
import stat
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = (ROOT / "meta-secureedge-platform/recipes-bsp/secureedge-rauc-backend"
           / "files/secureedge-rauc-backend")
FIXTURES = Path(__file__).with_name("fixtures")


class BackendFixtureMixin:
    def setUp(self):
        super().setUp()
        temporary = tempfile.TemporaryDirectory(prefix="secureedge-backend-", dir="/tmp")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.states = self.directory / "bootstate"
        self.states.mkdir()
        self.autoboot = self.directory / "autoboot.txt"
        self.cmdline = self.directory / "cmdline.txt"
        self.configure_boot(2, 3, "system0", 5)
        (self.states / "system0").write_text("good\n")
        (self.states / "system1").write_text("bad\n")

        tools = self.directory / "bin"
        tools.mkdir()
        sync = tools / "sync"
        sync.write_text("#!/bin/sh\nexit 0\n")
        sync.chmod(0o700)
        self.environment = {
            "PATH": str(tools) + os.pathsep + os.defpath,
            "LC_ALL": "C",
            "HOME": str(self.directory),
            "TMPDIR": str(self.directory),
            "SECUREEDGE_TEST_MODE": "1",
            "SECUREEDGE_BOOTCTL_DIR": str(self.directory),
            "SECUREEDGE_STATE_DIR": str(self.states),
            "SECUREEDGE_CMDLINE_FILE": str(self.cmdline),
        }

    def configure_boot(self, normal, trial, running, root):
        self.autoboot.write_text(
            "[all]\ntryboot_a_b=1\n"
            f"boot_partition={normal}\n[tryboot]\nboot_partition={trial}\n"
        )
        self.cmdline.write_text(f"root=/dev/mmcblk0p{root} rauc.slot={running}\n")

    def invoke(self, *args, simulation=True):
        environment = self.environment.copy()
        environment["SECUREEDGE_TEST_MODE"] = "1" if simulation else "0"
        return subprocess.run(
            ["/bin/sh", str(BACKEND), *args],
            cwd=self.directory, env=environment, capture_output=True,
            text=True, timeout=5, check=False,
        )

    def fixture_snapshot(self):
        snapshot = {}
        for path in sorted(self.directory.rglob("*")):
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                payload = os.readlink(path)
            elif stat.S_ISREG(mode):
                payload = path.read_bytes()
            else:
                payload = None
            snapshot[str(path.relative_to(self.directory))] = (mode, payload)
        return snapshot

    def assert_rejected(self, args, reason):
        before = self.fixture_snapshot()
        result = self.invoke(*args)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, f"secureedge-rauc-backend: {reason}\n")
        self.assertEqual(self.fixture_snapshot(), before, "Rejected command changed fixture state")
