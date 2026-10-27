#!/usr/bin/env bash
set -euo pipefail

# SecureEdge - offline provisioning of an already-flashed Raspberry Pi DEV card.
# Usage:
#   sudo ./scripts/provision-rpi-dev.sh ROOT_MOUNT BOOT_MOUNT WPA_FILE SSH_PUBLIC_KEY MQTT_HOST
# Never store the WPA file or any private SSH key in Git.

fail() {
    printf 'ERREUR : %s\n' "$*" >&2
    exit 1
}

if (( $# != 5 )); then
    printf 'Usage : sudo %s ROOT_MOUNT BOOT_MOUNT WPA_FILE SSH_PUBLIC_KEY MQTT_HOST\n' "$0" >&2
    exit 2
fi

(( EUID == 0 )) || fail 'executer avec sudo (sur le PC Ubuntu, carte SD montee).'

ROOT="$(realpath -e -- "$1")" || fail 'montage root introuvable.'
BOOT="$(realpath -e -- "$2")" || fail 'montage boot introuvable.'
WPA_SOURCE="$(realpath -e -- "$3")" || fail 'fichier WPA introuvable.'
SSH_PUBLIC_KEY="$(realpath -e -- "$4")" || fail 'cle SSH publique introuvable.'
MQTT_HOST="$5"

[[ "$ROOT" != "$BOOT" ]] || fail 'boot et root ne peuvent pas etre identiques.'
mountpoint -q -- "$ROOT" || fail 'ROOT doit etre un point de montage.'
mountpoint -q -- "$BOOT" || fail 'BOOT doit etre un point de montage.'

# Fail closed: provisioning is permitted only on two partitions of one USB reader.
ROOT_DEVICE="$(findmnt -n -o SOURCE --mountpoint "$ROOT")"
BOOT_DEVICE="$(findmnt -n -o SOURCE --mountpoint "$BOOT")"
[[ "$ROOT_DEVICE" == /dev/* && "$BOOT_DEVICE" == /dev/* ]] || fail 'sources de partitions inattendues.'
ROOT_PARENT="$(lsblk -dnro PKNAME "$ROOT_DEVICE")"
BOOT_PARENT="$(lsblk -dnro PKNAME "$BOOT_DEVICE")"
[[ -n "$ROOT_PARENT" && "$ROOT_PARENT" == "$BOOT_PARENT" ]] || fail 'les partitions ne sont pas sur le meme peripherique.'
[[ "$(lsblk -dnro TRAN "/dev/$ROOT_PARENT")" == usb ]] || fail 'peripherique non USB : operation refusee.'
[[ "$(findmnt -n -o FSTYPE --mountpoint "$ROOT")" == ext4 ]] || fail 'ROOT doit etre de type ext4.'
[[ "$(findmnt -n -o FSTYPE --mountpoint "$BOOT")" == vfat ]] || fail 'BOOT doit etre de type vfat.'

[[ -s "$WPA_SOURCE" && -s "$SSH_PUBLIC_KEY" ]] || fail 'le fichier Wi-Fi ou la cle publique est vide.'
ssh-keygen -lf "$SSH_PUBLIC_KEY" >/dev/null 2>&1 || fail 'fichier de cle publique SSH invalide.'
[[ "$MQTT_HOST" =~ ^[[:alnum:]][[:alnum:].-]*$ ]] || fail 'nom DNS ou IP du broker invalide.'

[[ -f "$ROOT/etc/os-release" ]] || fail 'rootfs Linux introuvable.'
grep -qx 'ID=secureedge' "$ROOT/etc/os-release" || fail 'cette rootfs ne semble pas etre SecureEdge.'
AGENT_CONFIG="$ROOT/etc/secureedge/agent.conf"
[[ -f "$AGENT_CONFIG" && -f "$BOOT/config.txt" ]] || fail 'configuration SecureEdge ou config.txt introuvable.'
grep -q '^mqtt_host=' "$AGENT_CONFIG" || fail 'mqtt_host absent du fichier agent.conf.'
[[ -f "$ROOT/usr/lib/systemd/system/wpa_supplicant@.service" || -f "$ROOT/lib/systemd/system/wpa_supplicant@.service" ]] || fail 'template wpa_supplicant absent de la rootfs.'

echo '[1/5] Installation du Wi-Fi (permissions 0600)'
install -d -o root -g root -m 0755 "$ROOT/etc/wpa_supplicant"
install -o root -g root -m 0600 "$WPA_SOURCE" "$ROOT/etc/wpa_supplicant/wpa_supplicant-wlan0.conf"

echo '[2/5] Installation de la cle SSH publique'
install -d -o root -g root -m 0700 "$ROOT/root/.ssh"
install -o root -g root -m 0600 "$SSH_PUBLIC_KEY" "$ROOT/root/.ssh/authorized_keys"

echo '[3/5] Adresse MQTT et periode d acquisition'
sed -i \
    -e "s/^mqtt_host=.*/mqtt_host=$MQTT_HOST/" \
    -e 's/^sampling_interval=.*/sampling_interval=5/' \
    "$AGENT_CONFIG"

echo '[4/5] Activation du service Wi-Fi pour le prochain boot'
systemctl --root="$ROOT" enable wpa_supplicant@wlan0.service

echo '[5/5] Selection du noyau ARM64 dans config.txt'
if ! grep -qx '# SecureEdge DEV provisioning' "$BOOT/config.txt"; then
    cat >> "$BOOT/config.txt" <<'EOF'

# SecureEdge DEV provisioning
[all]
arm_64bit=1
kernel=kernel8.img
EOF
fi

sync
printf 'Provisionnement DEV termine : %s et %s\n' "$ROOT_DEVICE" "$BOOT_DEVICE"
printf 'Demonter les partitions avant de retirer la microSD.\n'
