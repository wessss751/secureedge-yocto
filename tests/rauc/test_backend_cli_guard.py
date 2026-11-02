import unittest

from backend_test_support import BackendFixtureMixin


class BackendCliGuardTests(BackendFixtureMixin, unittest.TestCase):
    def test_unknown_command(self):
        self.assert_rejected(("unknown-command",), "Unknown command: unknown-command")

    def test_invalid_primary_slot(self):
        self.assert_rejected(("set-primary", "invalid-slot"), "Invalid slot: invalid-slot")

    def test_missing_primary_argument(self):
        self.assert_rejected(("set-primary",), "Usage: set-primary SLOT")

    def test_invalid_state_slot(self):
        self.assert_rejected(
            ("set-state", "invalid-slot", "good"), "Invalid slot: invalid-slot"
        )

    def test_invalid_state_value(self):
        self.assert_rejected(("set-state", "system1", "invalid"), "Invalid state: invalid")

    def test_unknown_state_slot(self):
        self.assert_rejected(("get-state", "invalid-slot"), "Invalid slot: invalid-slot")


if __name__ == "__main__":
    unittest.main()
