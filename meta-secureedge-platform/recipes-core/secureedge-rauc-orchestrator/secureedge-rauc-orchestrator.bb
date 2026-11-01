SUMMARY = "SecureEdge RAUC installation coordinator"
LICENSE = "CLOSED"

SRC_URI = "file://secureedge-rauc-orchestrator file://secureedge-rauc-transaction-check"

S = "${WORKDIR}"

do_install() {
    install -d "${D}${sbindir}"

    install -m 0755 \
        "${WORKDIR}/secureedge-rauc-orchestrator" \
        "${D}${sbindir}/secureedge-rauc-orchestrator"
}


do_install:append() {
    install -m 0755 \
        "${WORKDIR}/secureedge-rauc-transaction-check" \
        "${D}${sbindir}/secureedge-rauc-transaction-check"
}

FILES:${PN} = "${sbindir}/secureedge-rauc-orchestrator ${sbindir}/secureedge-rauc-transaction-check"

RDEPENDS:${PN} += "python3-core python3-modules rauc"
