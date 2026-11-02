import unittest

from backend_test_support import BackendFixtureMixin


class CustomBackendSafetyTests(BackendFixtureMixin, unittest.TestCase):
    def test_unknown_command_is_rejected(self):
        self.assert_rejected(("unknown-command",), "Unknown command: unknown-command")

    def test_invalid_primary_is_rejected(self):
        self.assert_rejected(("set-primary", "invalid-slot"), "Invalid slot: invalid-slot")

    def test_invalid_state_is_rejected(self):
        self.assert_rejected(
            ("set-state", "system1", "invalid-state"), "Invalid state: invalid-state"
        )

    def test_missing_slot_is_rejected(self):
        self.assert_rejected(("set-primary",), "Usage: set-primary SLOT")

    def test_extra_argument_is_rejected(self):
        self.assert_rejected(
            ("set-primary", "invalid-slot", "extra"), "Usage: set-primary SLOT"
        )


if __name__ == "__main__":
    unittest.main()
