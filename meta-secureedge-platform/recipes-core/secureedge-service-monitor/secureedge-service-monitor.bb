SUMMARY = "SecureEdge critical service health monitor"
DESCRIPTION = "Read-only critical systemd service verification"
LICENSE = "CLOSED"

SRC_URI = " \
    file://secureedge-service-monitor \
    file://secureedge-service-monitor.service \
    file://critical-services.units \
"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "secureedge-service-monitor.service"
SYSTEMD_AUTO_ENABLE:${PN} = "disable"

RDEPENDS:${PN} += "systemd"

do_install() {
    install -d ${D}${sbindir}
    install -d ${D}${sysconfdir}/secureedge
    install -d ${D}${systemd_system_unitdir}

    install -m 0755 \
        ${WORKDIR}/secureedge-service-monitor \
        ${D}${sbindir}/secureedge-service-monitor

    install -m 0644 \
        ${WORKDIR}/critical-services.units \
        ${D}${sysconfdir}/secureedge/critical-services.units

    install -m 0644 \
        ${WORKDIR}/secureedge-service-monitor.service \
        ${D}${systemd_system_unitdir}/secureedge-service-monitor.service
}

FILES:${PN} += " \
    ${sysconfdir}/secureedge/critical-services.units \
"
