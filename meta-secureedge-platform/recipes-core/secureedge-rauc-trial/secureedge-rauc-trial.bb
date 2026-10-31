SUMMARY = "SecureEdge RAUC trial boot preflight"
LICENSE = "CLOSED"

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
