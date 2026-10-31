# SecureEdge — BOOTCTL hardware acceptance gates

Target:
- Yocto Scarthgap
- Raspberry Pi Zero 2 W
- RAUC custom backend
- BOOTCTL: partition 1, FAT
- BOOT_A: partition 2
- BOOT_B: partition 3
- ROOTFS_A: partition 5
- ROOTFS_B: partition 6
- DATA: partition 7, ext4

## Boot safety invariant

Until successful trial confirmation, the previous known-good
slot must remain the normal boot target.

The firmware boot decision is made from autoboot.txt.

The active candidate must match both:
- the selected BOOT partition
- the Linux rootfs and RAUC slot identity

## Transaction requirements

- [ ] Exclusive transaction lock
- [ ] Protected root-owned transaction metadata
- [ ] Persistent transaction identifier
- [ ] Authenticated successful RAUC installation completion
- [ ] Consistent slot status across backend and DATA
- [ ] Idempotent recovery decision
- [ ] Power-loss-aware BOOTCTL write protocol
- [ ] BOOTCTL readback and integrity verification
- [ ] Firmware partition and tryboot identity verification
- [ ] Health gate completed before confirmation
- [ ] Recovery behavior validated after interrupted confirmation

## Failure injection matrix

| Interruption | Required behavior |
|---|---|
| Before installation | Previous system boots |
| During ROOTFS_B installation | A remains bootable |
| During BOOT_B installation | A remains bootable |
| After installation, before trial | A remains primary |
| During candidate trial boot | Normal reboot returns to A |
| Candidate health failure | B is not confirmed |
| Before BOOTCTL confirmation write | Previous primary is preserved |
| During BOOTCTL confirmation write | Deterministic recovery required |
| After BOOTCTL write, before journal commit | Reconcile journal and firmware |
| After confirmation, before normal reboot | New primary must be verifiable |
| During recovery | No undefined boot selection |

## FAT filesystem qualification

Journal fsync on DATA does not make FAT BOOTCTL writes atomic.

A successful laboratory rename does not establish power-cut
resilience on microSD.

The implementation must be tested with interruptions at each
critical write and synchronization boundary.

## OTA hardware activation

Current status: NO-GO.

A manual root shell, a pending-slot marker, or a valid RAUC
signature cannot bypass these gates.
