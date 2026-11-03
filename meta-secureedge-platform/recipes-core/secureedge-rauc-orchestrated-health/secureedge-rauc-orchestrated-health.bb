SUMMARY = "SecureEdge orchestrated RAUC trial health gate"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://secureedge-rauc-orchestrated-health"

S = "${WORKDIR}"

do_install() {
    install -d "${D}${sbindir}"

    install -m 0755 \
        "${WORKDIR}/secureedge-rauc-orchestrated-health" \
        "${D}${sbindir}/secureedge-rauc-orchestrated-health"
}

FILES:${PN} = "${sbindir}/secureedge-rauc-orchestrated-health"

RDEPENDS:${PN} += "python3-core python3-json secureedge-rauc-boot-proof"
