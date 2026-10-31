SUMMARY = "SecureEdge RAUC trial boot health gate"
LICENSE = "CLOSED"

SRC_URI = "file://secureedge-health-gate.sh"

S = "${WORKDIR}"

do_install() {
    install -d "${D}${sbindir}"
    install -m 0755 "${WORKDIR}/secureedge-health-gate.sh" \
        "${D}${sbindir}/secureedge-rauc-health-gate"
}

FILES:${PN} = "${sbindir}/secureedge-rauc-health-gate"

RDEPENDS:${PN} += "secureedge-rauc-backend"
