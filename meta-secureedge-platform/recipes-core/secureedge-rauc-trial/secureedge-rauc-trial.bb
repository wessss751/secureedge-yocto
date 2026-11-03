SUMMARY = "SecureEdge RAUC trial boot preflight"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://secureedge-rauc-trial"

S = "${WORKDIR}"

do_install() {
    install -d "${D}${sbindir}"

    install -m 0755 \
        "${WORKDIR}/secureedge-rauc-trial" \
        "${D}${sbindir}/secureedge-rauc-trial"
}

FILES:${PN} = "${sbindir}/secureedge-rauc-trial"

RDEPENDS:${PN} += "secureedge-rauc-backend"
