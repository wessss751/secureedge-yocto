SUMMARY = "SecureEdge production image for Raspberry Pi Zero 2 W"
DESCRIPTION = "Production-oriented SecureEdge Linux image with reduced development features"

require secureedge-image-rpi-dev.bb

IMAGE_FEATURES:remove = " \
    debug-tweaks \
    allow-empty-password \
    empty-root-password \
    allow-root-login \
    dbg-pkgs \
    dev-pkgs \
    tools-debug \
    tools-profile \
    tools-sdk \
"

EXTRA_IMAGE_FEATURES:remove = " \
    debug-tweaks \
    allow-empty-password \
    empty-root-password \
    allow-root-login \
    dbg-pkgs \
    dev-pkgs \
    tools-debug \
    tools-profile \
    tools-sdk \
"
IMAGE_INSTALL:append = " secureedge-hardening"
inherit extrausers

EXTRA_USERS_PARAMS:append = " \
    useradd -m -U -d /home/edgeadmin -s /bin/sh edgeadmin; \
"
IMAGE_INSTALL:append = " secureedge-admin-access"
secureedge_prod_enable_timewait() {
    test -e "${IMAGE_ROOTFS}${systemd_system_unitdir}/systemd-time-wait-sync.service" || {
        echo "SecureEdge PROD: systemd-time-wait-sync.service absent"
        exit 1
    }

    install -d \
        "${IMAGE_ROOTFS}${sysconfdir}/systemd/system/sysinit.target.wants"

    ln -sfn \
        "${systemd_system_unitdir}/systemd-time-wait-sync.service" \
        "${IMAGE_ROOTFS}${sysconfdir}/systemd/system/sysinit.target.wants/systemd-time-wait-sync.service"
}

ROOTFS_POSTPROCESS_COMMAND:append = " secureedge_prod_enable_timewait; "

IMAGE_INSTALL:append = "${@' secureedge-rauc-trial' if d.getVar('SECUREEDGE_RAUC_CUSTOM_TEST') == '1' else ''}"

IMAGE_INSTALL:append = "${@' secureedge-rauc-boot-proof' if (d.getVar('SECUREEDGE_RAUC_CUSTOM_TEST') == '1' or d.getVar('SECUREEDGE_RAUC_ORCHESTRATED') == '1') else ''}"

IMAGE_INSTALL:append = "${@' secureedge-rauc-orchestrated-health' if d.getVar('SECUREEDGE_RAUC_ORCHESTRATED') == '1' else ''}"

IMAGE_INSTALL:append = "${@' secureedge-rauc-orchestrator' if d.getVar('SECUREEDGE_RAUC_ORCHESTRATED') == '1' else ''}"
