SUMMARY = "SecureEdge RAUC trial boot health gate"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://secureedge-health-gate.sh"

S = "${WORKDIR}"

do_install() {
    install -d "${D}${sbindir}"
    install -m 0755 "${WORKDIR}/secureedge-health-gate.sh" \
        "${D}${sbindir}/secureedge-rauc-health-gate"
}

FILES:${PN} = "${sbindir}/secureedge-rauc-health-gate"

RDEPENDS:${PN} += "secureedge-rauc-backend"
