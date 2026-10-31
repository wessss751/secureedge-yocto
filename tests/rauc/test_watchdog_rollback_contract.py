import unittest


def rollback_decision(
    trial_boot,
    health_ok,
    watchdog_available,
    primary_unchanged,
):
    if not primary_unchanged:
        return "STOP_UNSAFE_PRIMARY"

    if not trial_boot:
        return "NORMAL_BOOT"

    if health_ok:
        return "ALLOW_CONFIRMATION_CHECKS"

    if watchdog_available:
        return "REQUEST_NORMAL_REBOOT"

    return "ROLLBACK_NOT_GUARANTEED"


class WatchdogRollbackTests(unittest.TestCase):

    def test_normal_boot(self):
        self.assertEqual(
            rollback_decision(False, True, True, True),
            "NORMAL_BOOT",
        )

    def test_trial_success(self):
        self.assertEqual(
            rollback_decision(True, True, True, True),
            "ALLOW_CONFIRMATION_CHECKS",
        )

    def test_trial_health_failure(self):
        self.assertEqual(
            rollback_decision(True, False, True, True),
            "REQUEST_NORMAL_REBOOT",
        )

    def test_watchdog_missing(self):
        self.assertEqual(
            rollback_decision(True, False, False, True),
            "ROLLBACK_NOT_GUARANTEED",
        )

    def test_primary_changed_early(self):
        self.assertEqual(
            rollback_decision(True, True, True, False),
            "STOP_UNSAFE_PRIMARY",
        )

    def test_primary_changed_on_failure(self):
        self.assertEqual(
            rollback_decision(True, False, True, False),
            "STOP_UNSAFE_PRIMARY",
        )


if __name__ == "__main__":
    unittest.main()
