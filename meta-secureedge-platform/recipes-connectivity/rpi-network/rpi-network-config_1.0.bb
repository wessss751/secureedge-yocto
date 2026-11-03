SUMMARY = "SecureEdge Raspberry Pi network configuration"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

inherit systemd

SRC_URI = " \
    file://20-wlan0.network \
    file://secureedge-network.service \
"

S = "${WORKDIR}"

SYSTEMD_SERVICE:${PN} = "secureedge-network.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

do_install() {
    install -d ${D}${sysconfdir}/systemd/network

    install -m 0644 ${WORKDIR}/20-wlan0.network \
        ${D}${sysconfdir}/systemd/network/20-wlan0.network

    install -d ${D}${systemd_system_unitdir}

    install -m 0644 ${WORKDIR}/secureedge-network.service \
        ${D}${systemd_system_unitdir}/secureedge-network.service
}

FILES:${PN} += " \
    ${sysconfdir}/systemd/network/20-wlan0.network \
    ${systemd_system_unitdir}/secureedge-network.service \
"

CONFFILES:${PN} += "${sysconfdir}/systemd/network/20-wlan0.network"
