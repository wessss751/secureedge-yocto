FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SRC_URI:append = " file://40-rauc-persistent.conf"

SECUREEDGE_RAUC_ORCHESTRATED ?= "0"

do_install:append() {
    if [ "${SECUREEDGE_RAUC_ORCHESTRATED}" = "1" ]; then
        install -d "${D}${systemd_system_unitdir}/secureedge-agent.service.d"

        install -m 0644 \
            "${WORKDIR}/40-rauc-persistent.conf" \
            "${D}${systemd_system_unitdir}/secureedge-agent.service.d/40-rauc-persistent.conf"
    fi
}

FILES:${PN}:append = " ${systemd_system_unitdir}/secureedge-agent.service.d/40-rauc-persistent.conf"
