SUMMARY = "SecureEdge production agent privilege isolation"
DESCRIPTION = "Dedicated service account and systemd sandbox"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

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
