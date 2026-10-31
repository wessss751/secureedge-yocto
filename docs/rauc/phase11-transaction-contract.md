# SecureEdge RAUC A/B transaction contract

## Scope

Target: Raspberry Pi Zero 2 W, Yocto Scarthgap.

BOOTCTL: p1
BOOT_A: p2
BOOT_B: p3
ROOTFS_A: p5
ROOTFS_B: p6
DATA: p7

## Transaction rules

1. Candidate must differ from the booted primary.
2. Recovery primary must be known-good.
3. A pending transaction must have an exclusive owner.
4. Installation completion must be proven by trusted RAUC state.
5. Slot identity must be verified before trial boot.
6. Trial boot must be a one-shot operation.
7. Candidate health must be proven before confirmation.
8. A failed trial must not promote the candidate.
9. BOOTCTL confirmation must have a qualified recovery protocol.
10. State changes must be consistent with the RAUC custom backend.

## Evidence required before each transition

STABLE -> INSTALLED:
- Verified signed bundle
- Completed RAUC installation
- Correct inactive slot group
- Rootfs and boot image installation confirmed

INSTALLED -> TRIAL_ARMED:
- Persistent pending transaction
- Valid primary and candidate mapping
- Stable recovery slot
- Valid BOOTCTL
- Controlled reboot executor

TRIAL_ARMED -> TRIAL_VERIFIED:
- Kernel root partition matches candidate
- RAUC slot identity matches candidate
- Firmware tryboot flag confirms trial
- Firmware boot partition matches candidate

TRIAL_VERIFIED -> COMMITTED:
- SecureEdge agent active
- MQTT mutual TLS operational
- Watchdog configuration verified
- BOOTCTL recovery protocol qualified
- Boot selector update verified

Failure:
- Candidate not promoted
- Previous primary preserved
- Transaction retained for diagnostics

## Hardware status

NO-GO until hardware code and recovery validation are complete.
