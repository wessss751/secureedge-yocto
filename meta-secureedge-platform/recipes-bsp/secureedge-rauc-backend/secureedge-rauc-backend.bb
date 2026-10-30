SUMMARY = "SecureEdge RAUC Raspberry Pi boot backend"
DESCRIPTION = "Custom boot selection backend for SecureEdge RAUC A/B"
LICENSE = "CLOSED"

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
