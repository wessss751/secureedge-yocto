SUMMARY = "SecureEdge read-only Raspberry Pi A/B boot proof"
LICENSE = "CLOSED"

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
