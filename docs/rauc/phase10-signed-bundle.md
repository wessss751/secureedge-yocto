# SecureEdge — Phase 10: Signed RAUC OTA Bundle

Platform: Raspberry Pi Zero 2 W
Yocto release: Scarthgap
RAUC compatible: secureedge-rpi-zero2w

## Cryptography

Signing identity: SecureEdge RAUC Development
Bundle format: verity
Trust anchor: SecureEdge RAUC development CA

Private signing keys are stored outside Git.

## Artifacts

- rootfs.ext4: Yocto root filesystem image
- boot.vfat: candidate Raspberry Pi boot partition image
- secureedge-10.1-ab-lab.raucb: signed laboratory bundle

## Validation checklist

- [ ] Signing certificate verified against embedded CA
- [ ] Private key matches signing certificate
- [ ] ROOTFS image verified
- [ ] BOOT filesystem verified
- [ ] Slot-specific boot configuration verified
- [ ] Complete bundle created successfully
- [ ] RAUC signature verified successfully
- [ ] SHA-256 checksum archived

## Remaining limitations

- Physical OTA installation not performed
- Real tryboot transition not validated
- Durable confirmation and power-loss recovery not validated
- Automatic hardware rollback not demonstrated
- Bidirectional A/B boot image generation not finalized

Do not use this laboratory bundle for production OTA.
