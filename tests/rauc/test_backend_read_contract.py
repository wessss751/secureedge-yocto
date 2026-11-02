import unittest

from backend_test_support import BackendFixtureMixin, FIXTURES
from bootctl_reader import read_bootctl


class BackendReadContractTests(BackendFixtureMixin, unittest.TestCase):
    def select_fixture(self, name):
        self.autoboot.write_bytes((FIXTURES / name).read_bytes())
        return read_bootctl(self.autoboot)

    def assert_read(self, args, expected):
        before = self.fixture_snapshot()
        result = self.invoke(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected + "\n")
        self.assertEqual(self.fixture_snapshot(), before)

    def test_primary_a(self):
        self.select_fixture("autoboot-a.txt")
        self.assert_read(("get-primary",), "system0")

    def test_primary_b(self):
        self.select_fixture("autoboot-b.txt")
        self.assert_read(("get-primary",), "system1")

    def test_primary_output_matches_rauc_contract(self):
        for name in ("autoboot-a.txt", "autoboot-b.txt"):
            with self.subTest(name=name):
                parsed = self.select_fixture(name)
                self.assert_read(("get-primary",), parsed["primary"])

    def test_trial_slot_is_not_primary(self):
        for name in ("autoboot-a.txt", "autoboot-b.txt"):
            with self.subTest(name=name):
                parsed = self.select_fixture(name)
                self.assertNotEqual(parsed["primary"], parsed["trial"])
                self.assert_read(("get-tryboot-target",), parsed["trial"])

    def test_state_vocabulary(self):
        boot = self.autoboot.read_bytes()
        for slot in ("system0", "system1"):
            other = "system1" if slot == "system0" else "system0"
            for state in ("good", "bad"):
                with self.subTest(slot=slot, state=state):
                    unchanged = (self.states / other).read_bytes()
                    result = self.invoke("set-state", slot, state)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(result.stderr, "")
                    self.assertEqual((self.states / slot).read_bytes(), (state + "\n").encode())
                    self.assertEqual((self.states / other).read_bytes(), unchanged)
                    self.assert_read(("get-state", slot), state)
                    self.assertEqual(self.autoboot.read_bytes(), boot)
                    self.assertFalse((self.states / "pending-slot").exists())
                    self.assertEqual(sorted(p.name for p in self.states.iterdir()), ["system0", "system1"])

    def test_invalid_state_is_rejected_without_changes(self):
        for state in ("unknown", "GOOD", ""):
            with self.subTest(state=state):
                self.assert_rejected(("set-state", "system1", state), f"Invalid state: {state}")

    def test_invalid_stored_state_is_rejected(self):
        (self.states / "system1").write_text("unknown\n")
        self.assert_rejected(("get-state", "system1"), "Invalid stored state for system1")


if __name__ == "__main__":
    unittest.main()
