import configparser
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]

FILES = (
    PROJECT
    / "meta-secureedge-platform"
    / "recipes-core"
    / "secureedge-watchdog"
    / "files"
)


def read_config(filename):
    parser = configparser.ConfigParser()
    with (FILES / filename).open() as stream:
        parser.read_file(stream)
    return parser["Manager"]


class WatchdogConfigTests(unittest.TestCase):

    def test_prod_watchdog_enabled(self):
        config = read_config("60-secureedge-watchdog.conf")
        self.assertEqual(config["RuntimeWatchdogSec"], "10s")

    def test_test_watchdog_enabled(self):
        config = read_config("60-secureedge-watchdog-test.conf")
        self.assertEqual(config["RuntimeWatchdogSec"], "10s")

    def test_watchdog_device(self):
        config = read_config("60-secureedge-watchdog-test.conf")
        self.assertEqual(config["WatchdogDevice"], "/dev/watchdog0")


    def test_recipe_installs_selected_payload(self):
        recipe = (FILES.parent / "secureedge-watchdog.bb").read_text()
        self.assertIn('SECUREEDGE_WATCHDOG_TEST ?= "0"', recipe)
        match = re.search(r"^do_install\(\) \{\n(.*?)^\}", recipe, re.M | re.S)
        self.assertIsNotNone(match, "Missing install task")
        # Exercise only this reviewed install body, with all destinations under /tmp.
        for flag, source in (("0", "60-secureedge-watchdog.conf"),
                             ("1", "60-secureedge-watchdog-test.conf")):
            with self.subTest(flag=flag), tempfile.TemporaryDirectory(dir="/tmp") as directory:
                result = subprocess.run(
                    ["/bin/sh", "-eu", "-c", match.group(1)],
                    cwd=directory,
                    env={"PATH": os.defpath, "LC_ALL": "C", "HOME": directory,
                         "D": directory, "sysconfdir": "/etc", "WORKDIR": str(FILES),
                         "SECUREEDGE_WATCHDOG_TEST": flag},
                    capture_output=True, text=True, timeout=5, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                installed = Path(directory) / "etc/systemd/system.conf.d/60-secureedge-watchdog.conf"
                self.assertEqual(installed.read_bytes(), (FILES / source).read_bytes())

    def test_watchdog_profile_selects_test_payload_for_prod(self):
        profile = (PROJECT / "kas/rpi-zero2-watchdog-test.yml").read_text()
        self.assertRegex(profile, r'SECUREEDGE_WATCHDOG_TEST:pn-secureedge-watchdog\s*=\s*"1"')
        self.assertRegex(profile, r'IMAGE_INSTALL:append:pn-secureedge-image-rpi-prod\s*=\s*" secureedge-watchdog"')


if __name__ == "__main__":
    unittest.main()
