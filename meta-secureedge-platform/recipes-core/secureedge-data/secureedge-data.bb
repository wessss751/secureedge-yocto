SUMMARY = "SecureEdge persistent DATA partition setup"
DESCRIPTION = "Mount and initialize persistent DATA for SecureEdge and RAUC"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://data.mount \
    file://secureedge-data-init.service \
    file://secureedge-data-init \
    file://rauc-data.conf \
"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE:${PN} = "data.mount secureedge-data-init.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

do_install() {
    # Mount point in the root filesystem
    install -d -m 0755 ${D}/data

    # systemd units
    install -d ${D}${systemd_system_unitdir}

    install -m 0644 \
        ${WORKDIR}/data.mount \
        ${D}${systemd_system_unitdir}/data.mount

    install -m 0644 \
        ${WORKDIR}/secureedge-data-init.service \
        ${D}${systemd_system_unitdir}/secureedge-data-init.service

    # RAUC service dependency
    install -d ${D}${systemd_system_unitdir}/rauc.service.d

    install -m 0644 \
        ${WORKDIR}/rauc-data.conf \
        ${D}${systemd_system_unitdir}/rauc.service.d/10-secureedge-data.conf

    # Initialization script
    install -d ${D}${sbindir}

    install -m 0755 \
        ${WORKDIR}/secureedge-data-init \
        ${D}${sbindir}/secureedge-data-init
}

FILES:${PN} += " \
    /data \
    ${sbindir}/secureedge-data-init \
    ${systemd_system_unitdir}/data.mount \
    ${systemd_system_unitdir}/secureedge-data-init.service \
    ${systemd_system_unitdir}/rauc.service.d/10-secureedge-data.conf \
"
