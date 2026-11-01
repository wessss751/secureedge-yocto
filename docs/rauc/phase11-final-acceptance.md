# SecureEdge — Phase 11 final acceptance

Target:
- Raspberry Pi Zero 2 W
- Yocto Scarthgap
- RAUC signed A/B OTA

## Build and integration

- [ ] RAUC orchestrated profile built
- [ ] Final trial launcher installed
- [ ] Final BOOTCTL confirmer installed
- [ ] Recovery services installed
- [ ] Device provisioning available on candidate B

## Transaction safety

- [ ] Trusted RAUC installation completion proof
- [ ] Persistent exclusive transaction
- [ ] Safe one-shot tryboot
- [ ] Valid firmware boot proof
- [ ] FAT BOOTCTL interruption recovery qualified
- [ ] Previous primary remains recoverable

## Hardware validation

- [ ] Current SD backup restore tested
- [ ] Authorized recovery access available
- [ ] RAUC signed bundle installed on B
- [ ] B boots through tryboot
- [ ] ROOTFS_B and firmware identity verified
- [ ] SecureEdge agent active on B
- [ ] MQTT mTLS and telemetry verified
- [ ] Hardware watchdog verified
- [ ] B confirmed as primary
- [ ] Normal reboot remains on B

## Final result

Phase 11 hardware acceptance: PENDING.

No physical OTA acceptance shall be claimed
before every mandatory check passes.
