# SecureEdge — Phase 9 Validation

Target: Raspberry Pi Zero 2 W
Yocto: Scarthgap
Update framework: RAUC

## Validated on hardware

- SecureEdge agent active
- MQTT mutual TLS authentication
- Hardware watchdog configured to 10 seconds
- Linux running from ROOTFS_A
- BOOTCTL A/B partition layout
- SSH and restricted administrative access

## Validated in laboratory

- RAUC custom backend interface
- Reading primary and current slots
- Reading slot states
- Preparing an inactive candidate
- Simulating tryboot firmware evidence
- Rendering A/B confirmation configuration
- Simulating BOOTCTL confirmation transaction

## Not yet validated on hardware

- RAUC signed bundle installation
- Real tryboot reboot into ROOTFS_B
- Durable BOOTCTL confirmation
- Recovery from interrupted FAT writes
- DATA/BOOTCTL transaction consistency
- Hardware automatic rollback
- Power-loss and watchdog-failure recovery

## Safety

The production image remains protected.
The RAUC custom test image must not be used for OTA
until the production boot transaction and recovery
protocol have been implemented and validated.

## Next milestone

Implement hardware-safe boot transactions, then create
and validate signed RAUC OTA bundles.
