import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'meta-secureedge-platform' / 'recipes-core' / 'secureedge-rauc-healthcheck' / 'files' / 'secureedge-rauc-healthcheck'

class HealthCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.backend = base / 'backend'
        self.backend.write_text('#!/bin/sh\necho verified-tryboot=system1\n')
        self.backend.chmod(0o755)
        self.systemctl = base / 'systemctl'
        self.systemctl.write_text('#!/bin/sh\n[ "$1" = is-active ] && [ "$2" = --quiet ] && [ "$3" = secureedge-test.service ] && [ "${UNIT_ACTIVE:-0}" = 1 ]\n')
        self.systemctl.chmod(0o755)
        self.mounts = base / 'mounts'
        self.mounts.write_text('/dev/mmcblk0p7 /data ext4 rw,noatime 0 0\n')
        self.units = base / 'units'
        self.units.write_text('# Critical service\nsecureedge-test.service\n')
        self.env = os.environ.copy()
        self.env.update({
            'SECUREEDGE_HEALTH_TEST_MODE': '1',
            'SECUREEDGE_HEALTH_BACKEND': str(self.backend),
            'SECUREEDGE_HEALTH_MOUNTS': str(self.mounts),
            'SECUREEDGE_HEALTH_UNITS': str(self.units),
            'SECUREEDGE_HEALTH_SYSTEMCTL': str(self.systemctl),
            'UNIT_ACTIVE': '1',
        })

    def run_check(self):
        return subprocess.run(['/bin/sh', str(SCRIPT)], env=self.env,
                              capture_output=True, text=True, check=False)

    def test_healthy(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'health-ready=system1')

    def test_reject_wrong_mount(self):
        self.mounts.write_text('/dev/mmcblk0p7 /other ext4 rw 0 0\n')
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_reject_wrong_filesystem(self):
        self.mounts.write_text('/dev/mmcblk0p7 /data vfat rw 0 0\n')
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_reject_unhealthy_backend(self):
        self.backend.write_text('#!/bin/sh\nexit 1\n')
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_reject_invalid_backend_output(self):
        self.backend.write_text('#!/bin/sh\necho unexpected\n')
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_reject_inactive_service(self):
        self.env['UNIT_ACTIVE'] = '0'
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_reject_unconfigured_services(self):
        self.units.write_text('# no units\n')
        self.assertNotEqual(self.run_check().returncode, 0)

    def test_reject_invalid_unit_name(self):
        self.units.write_text('bad;command.service\n')
        self.assertNotEqual(self.run_check().returncode, 0)

if __name__ == '__main__':
    unittest.main()
