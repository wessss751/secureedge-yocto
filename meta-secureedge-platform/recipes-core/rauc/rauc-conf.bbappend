
FILESEXTRAPATHS:prepend := "${THISDIR}/files:"

SECUREEDGE_RAUC_CUSTOM_TEST ?= "0"

do_install:append() {
    if [ "${SECUREEDGE_RAUC_CUSTOM_TEST}" = "1" ]; then
        if [ -f "${D}${sysconfdir}/rauc/system.conf" ]; then
            conf="${D}${sysconfdir}/rauc/system.conf"
        elif [ -f "${D}${nonarch_libdir}/rauc/system.conf" ]; then
            conf="${D}${nonarch_libdir}/rauc/system.conf"
        else
            bbfatal "RAUC system.conf missing from known install paths"
        fi

        [ -f "$conf" ] || bbfatal "RAUC system.conf missing"

        grep -q '^bootloader=noop$' "$conf" \
            || bbfatal "Expected RAUC noop configuration"

        if grep -q '^\[handlers\]$' "$conf"; then
            bbfatal "RAUC handlers already exist: review configuration"
        fi

        sed -i 's/^bootloader=noop$/bootloader=custom/' "$conf"

        printf '\n[handlers]\nbootloader-custom-backend=/usr/sbin/secureedge-rauc-backend\n' \
            >> "$conf"
    fi
}


FILESEXTRAPATHS:prepend := "${THISDIR}/files:"
SRC_URI:append = " file://system-orchestrated.conf"

SECUREEDGE_RAUC_ORCHESTRATED ?= "0"

do_install:append() {
    if [ "${SECUREEDGE_RAUC_ORCHESTRATED}" = "1" ]; then
        if [ "${SECUREEDGE_RAUC_CUSTOM_TEST}" = "1" ]; then
            bbfatal "RAUC custom test and orchestrated modes are exclusive"
        fi

        if [ -f "${D}${sysconfdir}/rauc/system.conf" ]; then
            conf="${D}${sysconfdir}/rauc/system.conf"
        elif [ -f "${D}${nonarch_libdir}/rauc/system.conf" ]; then
            conf="${D}${nonarch_libdir}/rauc/system.conf"
        else
            bbfatal "Installed RAUC system.conf not found"
        fi

        install -m 0644 \
            "${WORKDIR}/system-orchestrated.conf" \
            "$conf"
    fi
}
