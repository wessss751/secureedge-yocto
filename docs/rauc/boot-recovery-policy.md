# SecureEdge — Boot Recovery Policy v1

## Platform

- Hardware: Raspberry Pi Zero 2 W
- Distribution: Yocto Scarthgap
- Boot mechanism: Raspberry Pi firmware + autoboot.txt
- Update framework: RAUC
- Stable baseline: system0
- Current bootloader mode: noop

## Recovery objectives

1. Never overwrite the stable boot and rootfs partitions during a candidate update.
2. Never confirm an unverified trial boot.
3. Keep BOOTCTL read-only outside narrowly controlled maintenance operations.
4. Preserve DATA across updates.
5. Reject inconsistent boot evidence and incomplete transactions.
6. Provide an offline microSD recovery procedure.

## Failure classes

| Failure | Policy |
|---|---|
| Candidate healthcheck failure | Do not promote candidate; request a normal reboot |
| Candidate kernel boot failure | Require a reset/reboot mechanism; verify return to stable slot |
| Candidate userspace hang | Require a tested watchdog strategy |
| Incomplete transaction journal | Reject further promotion and enter recovery handling |
| Invalid autoboot.txt | No automatic recovery guarantee; offline repair may be required |
| BOOTCTL filesystem corruption | Stop updates and require controlled recovery |
| Stable slot corruption | Recovery image or external maintenance required |

## Mandatory production gates

- Hardware validation of A and B boot paths
- Trusted trial-boot evidence
- Healthcheck with explicit service requirements
- Exclusive confirmation transaction
- Power-failure testing on the real storage medium
- Recovery test from a separate Ubuntu host
- No production OTA until these tests pass

## Current restrictions

- Do not enable RAUC custom bootloader yet.
- Do not trigger a real tryboot reboot yet.
- Do not write to BOOTCTL on the running Raspberry Pi.
- Do not claim automatic recovery from arbitrary FAT corruption.

## Recovery authority

An administrator with physical access to the device and a trusted recovery image must be able to inspect, repair or replace the microSD without requiring the installed Linux system to boot.
