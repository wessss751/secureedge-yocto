SUMMARY = "SecureEdge development image for ARM64"
DESCRIPTION = "Development image for the SecureEdge industrial embedded Linux platform."
LICENSE = "MIT"

require recipes-core/images/core-image-minimal.bb

IMAGE_INSTALL:append = " \
    bash \
    coreutils \
    iproute2 \
    iputils \
    procps \
"

IMAGE_FEATURES += "ssh-server-dropbear"
