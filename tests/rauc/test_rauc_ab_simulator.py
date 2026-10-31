import unittest

from rauc_ab_simulator import ABModel, BootError


class RaucABSimulationTests(unittest.TestCase):

    def setUp(self):
        self.model = ABModel()

    def test_initial_slot_a(self):
        self.assertEqual(self.model.primary, "system0")
        self.assertEqual(self.model.booted, "system0")

    def test_prepare_b_does_not_change_primary(self):
        self.model.prepare("system1")
        self.assertEqual(self.model.primary, "system0")
        self.assertEqual(self.model.states["system1"], "bad")

    def test_tryboot_b(self):
        self.model.prepare("system1")
        self.model.tryboot()
        self.assertEqual(self.model.booted, "system1")
        self.assertEqual(self.model.primary, "system0")

    def test_confirmation_requires_health(self):
        self.model.prepare("system1")
        self.model.tryboot()

        with self.assertRaises(BootError):
            self.model.confirm()

        self.assertEqual(self.model.primary, "system0")

    def test_successful_confirmation(self):
        self.model.prepare("system1")
        self.model.tryboot()
        self.model.check_health(True)
        self.model.confirm()

        self.assertEqual(self.model.primary, "system1")
        self.assertEqual(self.model.states["system1"], "good")

    def test_failed_health_rolls_back(self):
        self.model.prepare("system1")
        self.model.tryboot()
        self.model.check_health(False)
        self.model.normal_reboot()

        self.assertEqual(self.model.booted, "system0")
        self.assertEqual(self.model.primary, "system0")
        self.assertEqual(self.model.states["system1"], "bad")

    def test_interruption_before_confirmation(self):
        self.model.prepare("system1")
        self.model.tryboot()
        self.model.check_health(True)
        self.model.normal_reboot()

        self.assertEqual(self.model.booted, "system0")
        self.assertEqual(self.model.primary, "system0")

    def test_invalid_slot_rejected(self):
        with self.assertRaises(BootError):
            self.model.prepare("invalid-slot")

    def test_primary_slot_cannot_be_trial_target(self):
        with self.assertRaises(BootError):
            self.model.prepare("system0")

    def test_b_to_a_rollback(self):
        self.model.prepare("system1")
        self.model.tryboot()
        self.model.check_health(True)
        self.model.confirm()

        self.model.prepare("system0")
        self.model.tryboot()
        self.model.check_health(False)
        self.model.normal_reboot()

        self.assertEqual(self.model.primary, "system1")
        self.assertEqual(self.model.booted, "system1")


if __name__ == "__main__":
    unittest.main()
