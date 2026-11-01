# SecureEdge RAUC — Hardware Architecture Decision

Target: Raspberry Pi Zero 2 W, Yocto Scarthgap.

## Verified

- Signed RAUC A/B bundle
- BOOT_A and BOOT_B partition mapping
- ROOTFS_A and ROOTFS_B partition mapping
- BOOT_B cmdline points to ROOTFS_B
- Current microSD backup
- Offline FAT BOOTCTL update and readback
- Offline transaction state machine
- Read-only firmware and Linux boot identity verification

## Critical design choice

Option A:
RAUC custom bootloader backend with a genuinely functional
set-primary implementation and a qualified recovery protocol.

Option B:
RAUC noop backend used only for image installation, combined
with an external SecureEdge tryboot and confirmation
orchestrator. The orchestrator owns the boot transaction.

The two models must not be mixed implicitly.

## Production activation requirements

- [ ] Chosen RAUC integration model implemented
- [ ] Verified successful installation of entire inactive group
- [ ] Protected and persistent transaction identity
- [ ] Safe one-shot firmware trial trigger
- [ ] Trial boot identity checked against hardware firmware state
- [ ] Candidate health and provisioning validated
- [ ] BOOTCTL confirmation recovery qualified against interruption
- [ ] Previous stable slot remains recoverable
- [ ] Successful normal reboot after confirmation
- [ ] Real rollback demonstrated

## Current conclusion

Hardware OTA: NO-GO.

The boot proof verifier does not install, reboot, or confirm.
No real BOOTCTL writes are authorized.
