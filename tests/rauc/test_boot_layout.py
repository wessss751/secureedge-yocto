
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check_boot_layout.py")

spec = importlib.util.spec_from_file_location(
    "secureedge_boot_layout", SCRIPT
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BootLayoutTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            prefix="secureedge-layout-"
        )
        self.addCleanup(self.temp.cleanup)

        self.base = Path(self.temp.name)

        for name in ("BOOTCTL", "BOOT_A", "BOOT_B"):
            (self.base / name).mkdir()

        self.write_autoboot(2, 3)

        for slot, index, rootpart in (
            ("A", "system0", 5),
            ("B", "system1", 6),
        ):
            boot = self.base / f"BOOT_{slot}"

            for name in (
                "kernel8.img",
                "config.txt",
                "bcm2710-rpi-zero-2.dtb",
            ):
                (boot / name).write_bytes(b"fixture")

            (boot / "cmdline.txt").write_text(
                f"root=/dev/mmcblk0p{rootpart} "
                f"rootfstype=ext4 rootwait "
                f"rauc.slot={index}\n"
            )

    def write_autoboot(self, normal, trial):
        (self.base / "BOOTCTL/autoboot.txt").write_text(
            "[all]\n"
            "tryboot_a_b=1\n"
            f"boot_partition={normal}\n\n"
            "[tryboot]\n"
            f"boot_partition={trial}\n"
        )

    def validate(self):
        return module.validate(self.base)

    def test_normal_a_layout(self):
        result = self.validate()
        self.assertTrue(result["valid"])
        self.assertEqual(result["normal_partition"], 2)
        self.assertEqual(result["trial_partition"], 3)

    def test_normal_b_layout(self):
        self.write_autoboot(3, 2)
        result = self.validate()
        self.assertTrue(result["valid"])
        self.assertEqual(result["normal_partition"], 3)

    def test_same_partition_rejected(self):
        self.write_autoboot(2, 2)
        with self.assertRaises(ValueError):
            self.validate()

    def test_invalid_partition_rejected(self):
        self.write_autoboot(7, 3)
        with self.assertRaises(ValueError):
            self.validate()

    def test_missing_kernel_rejected(self):
        (self.base / "BOOT_B/kernel8.img").unlink()
        with self.assertRaises(ValueError):
            self.validate()

    def test_empty_dtb_rejected(self):
        (self.base / "BOOT_A/bcm2710-rpi-zero-2.dtb").write_bytes(b"")
        with self.assertRaises(ValueError):
            self.validate()

    def test_wrong_rootfs_b_rejected(self):
        (self.base / "BOOT_B/cmdline.txt").write_text(
            "root=/dev/mmcblk0p5 rauc.slot=system1\n"
        )
        with self.assertRaises(ValueError):
            self.validate()

    def test_wrong_slot_a_rejected(self):
        (self.base / "BOOT_A/cmdline.txt").write_text(
            "root=/dev/mmcblk0p5 rauc.slot=system1\n"
        )
        with self.assertRaises(ValueError):
            self.validate()

    def test_duplicate_section_rejected(self):
        path = self.base / "BOOTCTL/autoboot.txt"
        with path.open("a") as stream:
            stream.write("\n[all]\nboot_partition=2\n")
        with self.assertRaises(ValueError):
            self.validate()

    def test_symlink_kernel_rejected(self):
        kernel = self.base / "BOOT_B/kernel8.img"
        kernel.unlink()
        kernel.symlink_to(self.base / "BOOT_A/kernel8.img")
        with self.assertRaises(ValueError):
            self.validate()


if __name__ == "__main__":
    unittest.main()
