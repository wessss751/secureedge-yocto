# SecureEdge watchdog hardware validation plan

## Platform
- Raspberry Pi Zero 2 W
- Yocto Scarthgap
- Kernel 6.6.63-v8
- Driver bcm2835-wdt
- Stable slot system0

## Preconditions
- Development microSD available
- Recovery image available
- Physical access to Raspberry Pi
- BOOTCTL configuration backed up
- No OTA installation in progress
- RuntimeWatchdogSec initially 0

## Required tests
1. Confirm watchdog device and driver.
2. Confirm effective runtime timeout before testing.
3. Check systemd watchdog ownership.
4. Verify normal operation without unexpected resets.
5. Perform controlled recovery testing on development media.
6. Confirm the device boots after a watchdog-induced reset.
7. Verify DATA persistence.
8. Verify BOOTCTL consistency.
9. Verify slot selection.
10. Record results and failures.

## Restrictions
- Do not modify stable BOOTCTL during watchdog tests.
- Do not use production credentials in test images.
- Do not trigger kernel panic on the stable installation.
- Do not claim rollback success without a real trial-boot test.
