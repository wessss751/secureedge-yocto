SUMMARY = "SecureEdge industrial gateway agent"
DESCRIPTION = "Modular C application for the SecureEdge embedded Linux platform."
LICENSE = "CLOSED"
DEPENDS += "mosquitto"
SRC_URI = " \
    file://Makefile \
    file://src/main.c \
    file://src/agent.c \
    file://src/logger.c \
    file://include/agent.h \
    file://include/logger.h \
    file://src/sensor.c \
    file://include/sensor.h \
    file://src/mqtt_client.c \
    file://include/mqtt_client.h \
    file://secureedge-agent.service \
"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "secureedge-agent.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_compile() {
    oe_runmake \
        CC="${CC}" \
        CPPFLAGS="${CPPFLAGS}" \
        CFLAGS="${CFLAGS}" \
        LDFLAGS="${LDFLAGS}"
}

do_install() {
    install -d ${D}${bindir}

    install -m 0755 ${S}/secureedge-agent \
        ${D}${bindir}/secureedge-agent

    install -d ${D}${systemd_system_unitdir}

    install -m 0644 ${WORKDIR}/secureedge-agent.service \
        ${D}${systemd_system_unitdir}/secureedge-agent.service
}

FILES:${PN} += "${systemd_system_unitdir}/secureedge-agent.service"

