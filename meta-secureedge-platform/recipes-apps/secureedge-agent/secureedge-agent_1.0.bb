SUMMARY = "SecureEdge industrial gateway agent"
DESCRIPTION = "Modular C application for the SecureEdge embedded Linux platform."
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"
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
    file://src/config.c \
    file://include/config.h \
    file://config/agent.conf \
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
    install -d ${D}${sysconfdir}/secureedge

    install -m 0644 ${S}/config/agent.conf \
        ${D}${sysconfdir}/secureedge/agent.conf
}

FILES:${PN} += "${systemd_system_unitdir}/secureedge-agent.service"
CONFFILES:${PN} += "${sysconfdir}/secureedge/agent.conf"
