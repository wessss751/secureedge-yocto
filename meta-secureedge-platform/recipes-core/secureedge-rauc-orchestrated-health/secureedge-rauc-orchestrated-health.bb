SUMMARY = "SecureEdge orchestrated RAUC trial health gate"
LICENSE = "CLOSED"

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
