SUMMARY = "SecureEdge read-only BOOTCTL mount"
DESCRIPTION = "Mount Raspberry Pi A/B boot control partition safely"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

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
