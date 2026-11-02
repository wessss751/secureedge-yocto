import unittest


from backend_test_support import BackendFixtureMixin


class BackendSetPrimaryTests(BackendFixtureMixin, unittest.TestCase):
    def backend(self, *args, simulation=True):
        return self.invoke(*args, simulation=simulation)

    def test_prepare_a_to_b(self):
        before = self.autoboot.read_bytes()

        result = self.backend("set-primary", "system1")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.states / "pending-slot").read_text().strip(),
            "system1",
        )
        self.assertEqual(self.autoboot.read_bytes(), before)

        primary = self.backend("get-primary")
        self.assertEqual(primary.stdout.strip(), "system0")

    def test_prepare_b_to_a(self):
        self.configure_boot(3, 2, "system1", 6)

        (self.states / "system0").write_text("bad\n")
        (self.states / "system1").write_text("good\n")

        before = self.autoboot.read_bytes()

        result = self.backend("set-primary", "system0")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (self.states / "pending-slot").read_text().strip(),
            "system0",
        )
        self.assertEqual(self.autoboot.read_bytes(), before)

        primary = self.backend("get-primary")
        self.assertEqual(primary.stdout.strip(), "system1")

    def test_reject_active_slot(self):
        result = self.backend("set-primary", "system0")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.states / "pending-slot").exists())

    def test_reject_unknown_slot(self):
        result = self.backend("set-primary", "system9")
        self.assertNotEqual(result.returncode, 0)

    def test_reject_unhealthy_normal_slot(self):
        (self.states / "system0").write_text("bad\n")
        result = self.backend("set-primary", "system1")
        self.assertNotEqual(result.returncode, 0)

    def test_reject_wrong_running_slot(self):
        self.configure_boot(2, 3, "system1", 6)
        result = self.backend("set-primary", "system1")
        self.assertNotEqual(result.returncode, 0)

    def test_reject_outside_simulation(self):
        result = self.backend(
            "set-primary",
            "system1",
            simulation=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.states / "pending-slot").exists())


if __name__ == "__main__":
    unittest.main()
