# SecureEdge — Phase 11: OTA A/B Hardware Validation

Platform: Raspberry Pi Zero 2 W
Yocto: Scarthgap
RAUC compatible: secureedge-rpi-zero2w

## Objective

Install a signed ROOTFS + BOOT update into inactive slot B,
perform a one-shot tryboot and confirm B after health checks.

## Existing validated hardware baseline

- ROOTFS_A booted
- SecureEdge agent running
- MQTT mutual TLS authentication successful
- Hardware watchdog enabled at 10 seconds
- SSH administration operational

## Preflight

- [ ] Complete signed ROOTFS + BOOT bundle available
- [ ] RAUC signature verified against embedded CA
- [ ] BOOT image supports the selected target slot
- [ ] Production-safe set-primary implemented
- [ ] Real tryboot launcher implemented and controlled
- [ ] Firmware and rootfs verification implemented
- [ ] Health gate implemented
- [ ] Durable confirmation and recovery implemented
- [ ] Fresh full-SD backup verified
- [ ] Offline restoration procedure available

## Hardware OTA

- [ ] ROOTFS_B updated successfully
- [ ] BOOT_B updated successfully
- [ ] A remains primary until confirmation
- [ ] Raspberry Pi starts B through tryboot
- [ ] Firmware reports expected trial partition
- [ ] Agent and watchdog healthy on B
- [ ] B confirmation completes
- [ ] Normal reboot returns to B as primary
- [ ] A remains available for recovery

## Current status

Hardware installation NOT YET AUTHORIZED.
Hardware tryboot and rollback NOT YET VALIDATED.

## Recovery

Preserve the stable SD backup and boot configuration.
Do not issue unverified writes to BOOTCTL or active slots.

## Phase 11 final acceptance criteria

- [ ] Safe hardware set-primary implementation
- [ ] Persistent and exclusive update transaction
- [ ] Controlled one-shot tryboot launcher
- [ ] Recovery-qualified BOOTCTL confirmation
- [ ] Candidate rootfs receives required device provisioning
- [ ] Signed bundle installed successfully in inactive B
- [ ] BOOT_B and ROOTFS_B verified after installation
- [ ] Firmware tryboot identity verified on B
- [ ] SecureEdge health gate passed on B
- [ ] BOOTCTL primary switched to B
- [ ] Normal reboot confirmed on B
- [ ] Stable A retained as recovery slot

Hardware OTA acceptance: PENDING.
Do not declare the system production-ready before all checks pass.
