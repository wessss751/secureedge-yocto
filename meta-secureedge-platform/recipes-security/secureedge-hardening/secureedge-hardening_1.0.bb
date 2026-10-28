SUMMARY = "SecureEdge production agent privilege isolation"
DESCRIPTION = "Dedicated service account and systemd sandbox"
LICENSE = "CLOSED"

SRC_URI = "file://30-prod-hardening.conf"
S = "${WORKDIR}"

inherit useradd

USERADD_PACKAGES = "${PN}"

USERADD_PARAM:${PN} = "--system --home-dir /nonexistent --no-create-home --shell /bin/false --user-group secureedge"

RDEPENDS:${PN} += "secureedge-agent"

do_install() {
    install -d ${D}${systemd_system_unitdir}/secureedge-agent.service.d

    install -m 0644 ${WORKDIR}/30-prod-hardening.conf \
        ${D}${systemd_system_unitdir}/secureedge-agent.service.d/30-prod-hardening.conf
}

FILES:${PN} += "${systemd_system_unitdir}/secureedge-agent.service.d/30-prod-hardening.conf"
