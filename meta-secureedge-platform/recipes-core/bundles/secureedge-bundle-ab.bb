SUMMARY = "SecureEdge signed A/B OTA bundle"
LICENSE = "MIT"

inherit bundle

RAUC_BUNDLE_COMPATIBLE = "secureedge-rpi-zero2w"
RAUC_BUNDLE_VERSION = "10.1-ab-lab"
RAUC_BUNDLE_FORMAT = "verity"

RAUC_BUNDLE_SLOTS = "rootfs"
RAUC_SLOT_rootfs = "secureedge-image-rpi-prod"
RAUC_SLOT_rootfs[fstype] = "ext4"
