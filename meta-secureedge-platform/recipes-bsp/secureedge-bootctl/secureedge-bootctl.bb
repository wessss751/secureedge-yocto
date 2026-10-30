SUMMARY = "SecureEdge read-only BOOTCTL mount"
DESCRIPTION = "Mount Raspberry Pi A/B boot control partition safely"

LICENSE = "CLOSED"

SRC_URI = "file://bootctl.mount"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "bootctl.mount"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

do_install() {
    install -d -m 0755 ${D}/bootctl

    install -d ${D}${systemd_system_unitdir}

    install -m 0644 \
        ${WORKDIR}/bootctl.mount \
        ${D}${systemd_system_unitdir}/bootctl.mount
}

FILES:${PN} += " \
    /bootctl \
    ${systemd_system_unitdir}/bootctl.mount \
"
