SUMMARY = "SecureEdge development image for ARM64"
DESCRIPTION = "Development image for the SecureEdge industrial embedded Linux platform."
LICENSE = "MIT"

require recipes-core/images/core-image-minimal.bb

IMAGE_INSTALL:append = " \
    bash \
    coreutils \
    iproute2 \
    iproute2-ss \
    iputils \
    procps \
    os-release \
    secureedge-agent \
"

IMAGE_FEATURES += "ssh-server-dropbear"
