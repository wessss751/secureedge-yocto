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

SRC_URI:append = " file://secureedge-rauc-target-verify"

do_install:append() {
    install -m 0755         "${WORKDIR}/secureedge-rauc-target-verify"         "${D}${sbindir}/secureedge-rauc-target-verify"
}

FILES:${PN}:append = " ${sbindir}/secureedge-rauc-target-verify"

# Signed-bundle-bound, read-only partition audit (no boot activation).
SRC_URI:append = " file://secureedge-rauc-signed-target-verify"
do_install:append() {
    install -m 0755 \
        "${WORKDIR}/secureedge-rauc-signed-target-verify" \
        "${D}${sbindir}/secureedge-rauc-signed-target-verify"
}
FILES:${PN}:append = " ${sbindir}/secureedge-rauc-signed-target-verify"
