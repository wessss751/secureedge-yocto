SUMMARY = "SecureEdge RAUC A/B boot configuration files"
DESCRIPTION = "Deploy Raspberry Pi A/B boot selection and rootfs command lines"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

inherit deploy

SRC_URI = " \
    file://autoboot.txt \
    file://cmdline-a.txt \
    file://cmdline-b.txt \
"

S = "${WORKDIR}"

do_deploy() {
    install -d ${DEPLOYDIR}/secureedge-rauc

    install -m 0644 ${WORKDIR}/autoboot.txt \
        ${DEPLOYDIR}/secureedge-rauc/autoboot.txt

    install -m 0644 ${WORKDIR}/cmdline-a.txt \
        ${DEPLOYDIR}/secureedge-rauc/cmdline-a.txt

    install -m 0644 ${WORKDIR}/cmdline-b.txt \
        ${DEPLOYDIR}/secureedge-rauc/cmdline-b.txt
}
addtask deploy after do_compile
