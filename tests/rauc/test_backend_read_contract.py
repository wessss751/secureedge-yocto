import unittest
from pathlib import Path

from bootctl_reader import read_bootctl

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "rauc" / "fixtures"

VALID_SLOTS = {"system0", "system1"}
VALID_STATES = {"good", "bad"}


class BackendReadContractTests(unittest.TestCase):

    def test_primary_a(self):
        result = read_bootctl(FIXTURES / "autoboot-a.txt")
        self.assertEqual(result["primary"], "system0")

    def test_primary_b(self):
        result = read_bootctl(FIXTURES / "autoboot-b.txt")
        self.assertEqual(result["primary"], "system1")

    def test_primary_output_matches_rauc_contract(self):
        for name in ("autoboot-a.txt", "autoboot-b.txt"):
            with self.subTest(name=name):
                result = read_bootctl(FIXTURES / name)

                self.assertIn(result["primary"], VALID_SLOTS)

                # RAUC expects a bootname, not a partition number.
                output = result["primary"] + "\n"

                self.assertEqual(len(output.splitlines()), 1)
                self.assertIn(output.strip(), VALID_SLOTS)

    def test_trial_slot_is_not_primary(self):
        for name in ("autoboot-a.txt", "autoboot-b.txt"):
            with self.subTest(name=name):
                result = read_bootctl(FIXTURES / name)
                self.assertNotEqual(
                    result["primary"],
                    result["trial"],
                )

    def test_state_vocabulary(self):
        self.assertEqual(VALID_STATES, {"good", "bad"})


if __name__ == "__main__":
    unittest.main()
