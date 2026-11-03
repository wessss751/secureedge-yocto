SUMMARY = "SecureEdge RAUC A/B trial-boot health checks"
DESCRIPTION = "Read-only validation of tryboot identity, DATA mount and critical services"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://secureedge-rauc-healthcheck \
    file://secureedge-rauc-healthcheck.service \
    file://rauc-healthcheck.units \
"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "secureedge-rauc-healthcheck.service"
SYSTEMD_AUTO_ENABLE:${PN} = "disable"
RDEPENDS:${PN} += "secureedge-data secureedge-rauc-backend"

do_install() {
    install -d ${D}${sbindir}
    install -m 0755 ${WORKDIR}/secureedge-rauc-healthcheck \
        ${D}${sbindir}/secureedge-rauc-healthcheck

    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/secureedge-rauc-healthcheck.service \
        ${D}${systemd_system_unitdir}/secureedge-rauc-healthcheck.service

    install -d ${D}${sysconfdir}/secureedge
    install -m 0644 ${WORKDIR}/rauc-healthcheck.units \
        ${D}${sysconfdir}/secureedge/rauc-healthcheck.units
}

FILES:${PN} += " \
    ${sbindir}/secureedge-rauc-healthcheck \
    ${systemd_system_unitdir}/secureedge-rauc-healthcheck.service \
    ${sysconfdir}/secureedge/rauc-healthcheck.units \
"
