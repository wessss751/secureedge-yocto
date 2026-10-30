import unittest


def confirmation_allowed(
    current,
    primary,
    candidate,
    tryboot,
    firmware_partition,
    health_ok,
):
    slots = {"system0": 2, "system1": 3}

    if current not in slots or primary not in slots:
        return False

    if candidate not in slots:
        return False

    return all([
        current == candidate,
        primary != candidate,
        tryboot is True,
        firmware_partition == slots[candidate],
        health_ok is True,
    ])


class BootConfirmationContractTests(unittest.TestCase):

    def test_successful_a_to_b(self):
        self.assertTrue(
            confirmation_allowed(
                "system1", "system0", "system1",
                True, 3, True
            )
        )

    def test_failed_healthcheck(self):
        self.assertFalse(
            confirmation_allowed(
                "system1", "system0", "system1",
                True, 3, False
            )
        )

    def test_normal_boot_must_not_confirm(self):
        self.assertFalse(
            confirmation_allowed(
                "system1", "system0", "system1",
                False, 3, True
            )
        )

    def test_wrong_firmware_partition(self):
        self.assertFalse(
            confirmation_allowed(
                "system1", "system0", "system1",
                True, 2, True
            )
        )

    def test_wrong_current_slot(self):
        self.assertFalse(
            confirmation_allowed(
                "system0", "system0", "system1",
                True, 3, True
            )
        )

    def test_successful_b_to_a(self):
        self.assertTrue(
            confirmation_allowed(
                "system0", "system1", "system0",
                True, 2, True
            )
        )

    def test_unknown_slot_rejected(self):
        self.assertFalse(
            confirmation_allowed(
                "unknown", "system0", "system1",
                True, 3, True
            )
        )


if __name__ == "__main__":
    unittest.main()
