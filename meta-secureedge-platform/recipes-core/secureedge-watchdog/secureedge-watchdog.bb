
SUMMARY = "SecureEdge hardware watchdog configuration"
DESCRIPTION = "Staged watchdog configuration for SecureEdge A/B"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://60-secureedge-watchdog.conf \
    file://60-secureedge-watchdog-test.conf \
"

S = "${WORKDIR}"

SECUREEDGE_WATCHDOG_TEST ?= "0"

do_install() {
    install -d ${D}${sysconfdir}/systemd/system.conf.d

    if [ "${SECUREEDGE_WATCHDOG_TEST}" = "1" ]; then
        install -m 0644 \
            ${WORKDIR}/60-secureedge-watchdog-test.conf \
            ${D}${sysconfdir}/systemd/system.conf.d/60-secureedge-watchdog.conf
    else
        install -m 0644 \
            ${WORKDIR}/60-secureedge-watchdog.conf \
            ${D}${sysconfdir}/systemd/system.conf.d/60-secureedge-watchdog.conf
    fi
}

FILES:${PN} += " \
    ${sysconfdir}/systemd/system.conf.d/60-secureedge-watchdog.conf \
"
