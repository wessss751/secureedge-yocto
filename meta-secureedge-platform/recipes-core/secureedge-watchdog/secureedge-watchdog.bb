
SUMMARY = "SecureEdge hardware watchdog configuration"
DESCRIPTION = "Staged watchdog configuration for SecureEdge A/B"
LICENSE = "CLOSED"

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
