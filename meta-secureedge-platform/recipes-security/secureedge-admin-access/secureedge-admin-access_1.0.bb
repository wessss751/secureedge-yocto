SUMMARY = "Restricted administration permissions for SecureEdge PROD"
DESCRIPTION = "Installs sudo and limited maintenance permissions for edgeadmin"
LICENSE = "CLOSED"

SRC_URI = "file://90-secureedge-edgeadmin"

S = "${WORKDIR}"

RDEPENDS:${PN} += "sudo"

do_install() {
    install -d -m 0750 ${D}${sysconfdir}/sudoers.d

    install -m 0440 \
        ${WORKDIR}/90-secureedge-edgeadmin \
        ${D}${sysconfdir}/sudoers.d/90-secureedge-edgeadmin
}

FILES:${PN} += "${sysconfdir}/sudoers.d/90-secureedge-edgeadmin"

CONFFILES:${PN} += "${sysconfdir}/sudoers.d/90-secureedge-edgeadmin"
