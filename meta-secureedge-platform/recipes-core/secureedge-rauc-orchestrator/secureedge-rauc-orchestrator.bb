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

# Hardware installation service: installed but never auto-enabled.
SRC_URI:append = " file://secureedge-rauc-install.service"

inherit systemd

SYSTEMD_SERVICE:${PN} = "secureedge-rauc-install.service"
SYSTEMD_AUTO_ENABLE:${PN} = "disable"

do_install:append() {
    install -d "${D}${systemd_system_unitdir}"

    install -m 0644 \
        "${WORKDIR}/secureedge-rauc-install.service" \
        "${D}${systemd_system_unitdir}/secureedge-rauc-install.service"
}

FILES:${PN}:append = " ${systemd_system_unitdir}/secureedge-rauc-install.service"

# Fail-closed A->B activation, hardware disabled until privileged lab approval.
SRC_URI:append = " file://secureedge-rauc-activation"
do_install:append() {
    install -m 0755 \
        "${WORKDIR}/secureedge-rauc-activation" \
        "${D}${sbindir}/secureedge-rauc-activation"
}
FILES:${PN}:append = " ${sbindir}/secureedge-rauc-activation"

# LAB-only BOOTCTL confirmation tool; deliberately no auto-enabled service.
SRC_URI:append = " file://secureedge-rauc-confirm-lab"
do_install:append() {
    install -m 0755 \
        "${WORKDIR}/secureedge-rauc-confirm-lab" \
        "${D}${sbindir}/secureedge-rauc-confirm-lab"
}
FILES:${PN}:append = " ${sbindir}/secureedge-rauc-confirm-lab"
