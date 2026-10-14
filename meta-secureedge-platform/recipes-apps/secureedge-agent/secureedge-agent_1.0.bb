
SUMMARY = "SecureEdge industrial gateway agent"
DESCRIPTION = "Initial C application for the SecureEdge embedded Linux platform."
LICENSE = "CLOSED"

SRC_URI = " \
    file://secureedge-agent.c \
    file://secureedge-agent.service \
"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "secureedge-agent.service"
SYSTEMD_AUTO_ENABLE = "enable"

do_compile() {
    ${CC} ${CFLAGS} ${LDFLAGS} secureedge-agent.c -o secureedge-agent
}

do_install() {
    install -d ${D}${bindir}
    install -m 0755 secureedge-agent ${D}${bindir}/secureedge-agent

    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/secureedge-agent.service \
        ${D}${systemd_system_unitdir}/secureedge-agent.service
}

FILES:${PN} += "${systemd_system_unitdir}/secureedge-agent.service"

