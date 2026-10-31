import configparser
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

    def test_prod_watchdog_disabled(self):
        config = read_config("60-secureedge-watchdog.conf")
        self.assertEqual(config["RuntimeWatchdogSec"], "0")

    def test_test_watchdog_enabled(self):
        config = read_config("60-secureedge-watchdog-test.conf")
        self.assertEqual(config["RuntimeWatchdogSec"], "10s")

    def test_watchdog_device(self):
        config = read_config("60-secureedge-watchdog-test.conf")
        self.assertEqual(config["WatchdogDevice"], "/dev/watchdog0")


if __name__ == "__main__":
    unittest.main()
