#!/usr/bin/env bash
# SecureEdge DEV: provision mTLS offline onto a freshly flashed Raspberry Pi USB microSD.
# Usage: sudo ./scripts/provision-rpi-mtls.sh ROOT_MOUNT PRIVATE_PKI_DIR BROKER_IPV4
set -euo pipefail
umask 077

usage() {
    printf 'Usage: sudo %s ROOT_MOUNT PRIVATE_PKI_DIR BROKER_IPV4\n' "$0" >&2
    exit 2
}

[[ $# -eq 3 ]] || usage
[[ ${EUID} -eq 0 ]] || { echo 'ERROR: run with sudo.' >&2; exit 1; }

ROOT="$(realpath -e -- "$1")"
PKI="$(realpath -e -- "$2")"
BROKER="$3"

# Prevent shell substitutions, invalid IPv4s, and accidental changes to /.
[[ "$ROOT" != / ]] || { echo 'ERROR: refusing to provision /.' >&2; exit 1; }
python3 - "$BROKER" <<'PY'
import ipaddress
import sys
try:
    ipaddress.IPv4Address(sys.argv[1])
except ipaddress.AddressValueError:
    sys.exit('ERROR: BROKER_IPV4 must be a valid IPv4 address.')
PY

mountpoint -q -- "$ROOT" || {
    echo 'ERROR: ROOT_MOUNT must be an actual mount point.' >&2
    exit 1
}
ROOT_DEV="$(findmnt -nr -o SOURCE --mountpoint "$ROOT")"
[[ -b "$ROOT_DEV" ]] || { echo 'ERROR: expected a block-device filesystem.' >&2; exit 1; }
PARENT="$(lsblk -dnro PKNAME "$ROOT_DEV")"
[[ -n "$PARENT" ]] || { echo 'ERROR: cannot identify parent disk.' >&2; exit 1; }
[[ "$(lsblk -dnro TRAN "/dev/$PARENT")" == usb ]] || {
    echo 'ERROR: refusing non-USB disk; do not provision the internal SSD.' >&2
    exit 1
}
[[ "$(findmnt -nr -o FSTYPE --mountpoint "$ROOT")" == ext4 ]] || {
    echo 'ERROR: expected an ext4 Linux root partition.' >&2
    exit 1
}

OS_RELEASE="$ROOT/etc/os-release"
CFG="$ROOT/etc/secureedge/agent.conf"
[[ -f "$OS_RELEASE" && -f "$CFG" && -f "$ROOT/usr/bin/secureedge-agent" ]] || {
    echo 'ERROR: missing SecureEdge Linux files on target rootfs.' >&2
    exit 1
}
grep -Eq '^ID="?secureedge"?$' "$OS_RELEASE" || {
    echo 'ERROR: target rootfs is not SecureEdge Linux.' >&2
    exit 1
}
grep -q '^mqtt_host=' "$CFG" && grep -q '^mqtt_port=' "$CFG" || {
    echo 'ERROR: agent.conf lacks mqtt_host or mqtt_port.' >&2
    exit 1
}

CA="$PKI/ca/ca.crt"
CERT="$PKI/clients/device01/device01.crt"
KEY="$PKI/clients/device01/device01.key"
for f in "$CA" "$CERT" "$KEY"; do
    [[ -s "$f" ]] || { echo "ERROR: required PKI file absent: $f" >&2; exit 1; }
done

# Verify the certificate chain and ensure the client key matches its certificate.
openssl verify -CAfile "$CA" -purpose sslclient "$CERT"
CERT_PUB="$(openssl x509 -in "$CERT" -pubkey -noout | openssl pkey -pubin -outform DER | sha256sum | cut -d' ' -f1)"
KEY_PUB="$(openssl pkey -in "$KEY" -pubout -outform DER | sha256sum | cut -d' ' -f1)"
[[ "$CERT_PUB" == "$KEY_PUB" ]] || {
    echo 'ERROR: device01 private key does not match its certificate.' >&2
    exit 1
}

echo "Provisioning SecureEdge mTLS on $ROOT_DEV (mounted at $ROOT)"
CERT_DIR="$ROOT/etc/secureedge/certs"
install -d -o root -g root -m 0700 "$CERT_DIR"
install -o root -g root -m 0644 "$CA" "$CERT_DIR/ca.crt"
install -o root -g root -m 0644 "$CERT" "$CERT_DIR/device01.crt"
install -o root -g root -m 0600 "$KEY" "$CERT_DIR/device01.key"

ENV_FILE="$ROOT/etc/secureedge/mqtt-tls.env"
cat > "$ENV_FILE" <<'EOF'
SECUREEDGE_MQTT_TLS=1
SECUREEDGE_MQTT_CA=/etc/secureedge/certs/ca.crt
SECUREEDGE_MQTT_CERT=/etc/secureedge/certs/device01.crt
SECUREEDGE_MQTT_KEY=/etc/secureedge/certs/device01.key
EOF
chown root:root "$ENV_FILE"
chmod 0600 "$ENV_FILE"

DROPIN="$ROOT/etc/systemd/system/secureedge-agent.service.d"
install -d -o root -g root -m 0755 "$DROPIN"
cat > "$DROPIN/20-mtls.conf" <<'EOF'
[Service]
EnvironmentFile=/etc/secureedge/mqtt-tls.env
EOF
chown root:root "$DROPIN/20-mtls.conf"
chmod 0644 "$DROPIN/20-mtls.conf"

# The host is an IPv4 literal, validated above (safe as a sed replacement).
sed -i \
    -e "s/^mqtt_host=.*/mqtt_host=$BROKER/" \
    -e 's/^mqtt_port=.*/mqtt_port=8883/' \
    "$CFG"

sync
echo 'SUCCESS: TLS CA/cert/key, environment, service drop-in and MQTT port 8883 provisioned.'
echo 'This does not install a TLS-capable binary: your Yocto image must already include it.'
echo 'Unmount all SD partitions before removing the card.'
