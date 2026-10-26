SUMMARY = "SecureEdge development image for Raspberry Pi Zero 2 W"

require secureedge-image-dev.bb

IMAGE_INSTALL:append = " \
    wpa-supplicant \
    rpi-network-config \
    linux-firmware-rpidistro-bcm43430 \
    linux-firmware-rpidistro-bcm43436 \
    linux-firmware-rpidistro-bcm43436s \
    kernel-module-brcmfmac \
    kernel-module-brcmfmac-wcc \
    kernel-module-brcmutil \
    kernel-module-cfg80211 \
"
