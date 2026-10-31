SUMMARY = "SecureEdge signed A/B OTA bundle"
LICENSE = "MIT"

inherit bundle

RAUC_BUNDLE_COMPATIBLE = "secureedge-rpi-zero2w"
RAUC_BUNDLE_VERSION = "10.1-ab-lab"
RAUC_BUNDLE_FORMAT = "verity"

# Initial integration: build the ROOTFS from Yocto.
RAUC_BUNDLE_SLOTS = "rootfs"
RAUC_SLOT_rootfs = "secureedge-image-rpi-prod"
RAUC_SLOT_rootfs[fstype] = "ext4"

# TODO before enabling the boot slot:
# - Provide a Yocto recipe that produces a verified boot.vfat.
# - Ensure slot-specific cmdline.txt and firmware layout.
# - Add boot to RAUC_BUNDLE_SLOTS.
# - Set RAUC_SLOT_boot and its file/dependencies.
#
# Signing credentials must be configured outside Git.
