
import configparser
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

AUTOBOOT = (
    ROOT
    / "meta-secureedge-platform"
    / "recipes-bsp"
    / "secureedge-rauc-bootfiles"
    / "files"
    / "autoboot.txt"
)


def read_boot_selection():
    config = configparser.ConfigParser(interpolation=None)

    if not config.read(AUTOBOOT):
        raise RuntimeError("Cannot read autoboot.txt")

    if config.getint("all", "tryboot_a_b") != 1:
        raise RuntimeError("tryboot_a_b must be enabled")

    normal = config.getint("all", "boot_partition")
    trial = config.getint("tryboot", "boot_partition")

    if (normal, trial) not in ((2, 3), (3, 2)):
        raise RuntimeError("Invalid A/B boot selection")

    return normal, trial


def prepare_trial(normal, trial, candidate):
    if candidate != trial or candidate == normal:
        raise ValueError("Candidate must be inactive")

    return normal, trial


def confirm_trial(normal, trial, booted, tryboot, healthy):
    if not (tryboot and healthy and booted == trial):
        raise ValueError("Trial cannot be confirmed")

    return trial, normal


class TrybootContractTests(unittest.TestCase):

    def test_autoboot_configuration(self):
        normal, trial = read_boot_selection()
        self.assertEqual({normal, trial}, {2, 3})

    def test_install_does_not_change_normal_boot(self):
        normal, trial = read_boot_selection()
        result = prepare_trial(normal, trial, trial)
        self.assertEqual(result[0], normal)

    def test_successful_trial_can_be_confirmed(self):
        normal, trial = read_boot_selection()
        result = confirm_trial(
            normal, trial,
            booted=trial,
            tryboot=True,
            healthy=True,
        )
        self.assertEqual(result, (trial, normal))

    def test_failed_health_check_is_rejected(self):
        normal, trial = read_boot_selection()
        with self.assertRaises(ValueError):
            confirm_trial(
                normal, trial,
                booted=trial,
                tryboot=True,
                healthy=False,
            )

    def test_normal_boot_cannot_confirm_trial(self):
        normal, trial = read_boot_selection()
        with self.assertRaises(ValueError):
            confirm_trial(
                normal, trial,
                booted=trial,
                tryboot=False,
                healthy=True,
            )

    def test_wrong_partition_is_rejected(self):
        normal, trial = read_boot_selection()
        with self.assertRaises(ValueError):
            confirm_trial(
                normal, trial,
                booted=normal,
                tryboot=True,
                healthy=True,
            )

    def test_invalid_candidate_is_rejected(self):
        normal, trial = read_boot_selection()
        with self.assertRaises(ValueError):
            prepare_trial(normal, trial, normal)


if __name__ == "__main__":
    unittest.main()
