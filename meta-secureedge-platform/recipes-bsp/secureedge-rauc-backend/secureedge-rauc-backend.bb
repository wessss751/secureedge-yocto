SUMMARY = "SecureEdge RAUC Raspberry Pi boot backend"
DESCRIPTION = "Custom boot selection backend for SecureEdge RAUC A/B"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://secureedge-rauc-backend"

S = "${WORKDIR}"

RDEPENDS:${PN} += "busybox"

do_install() {
    install -d ${D}${sbindir}

    install -m 0755 \
        ${WORKDIR}/secureedge-rauc-backend \
        ${D}${sbindir}/secureedge-rauc-backend
}

FILES:${PN} += "${sbindir}/secureedge-rauc-backend"
