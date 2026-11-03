SUMMARY = "SecureEdge read-only Raspberry Pi A/B boot proof"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://secureedge-rauc-boot-proof"

S = "${WORKDIR}"

do_install() {
    install -d "${D}${sbindir}"
    install -m 0755 \
        "${WORKDIR}/secureedge-rauc-boot-proof" \
        "${D}${sbindir}/secureedge-rauc-boot-proof"
}

FILES:${PN} = "${sbindir}/secureedge-rauc-boot-proof"

RDEPENDS:${PN} += "python3-core python3-modules"
