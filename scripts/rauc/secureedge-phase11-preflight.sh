#!/bin/sh
set -u

PROJECT="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
BASE="/mnt/secureedge-storage/rauc-ab-tests/bundles"
BUNDLE="$BASE/secureedge-10.1-ab-lab.raucb"
CA="$PROJECT/meta-secureedge-platform/recipes-core/rauc/files/ca.cert.pem"
BACKEND="$PROJECT/meta-secureedge-platform/recipes-bsp/secureedge-rauc-backend/files/secureedge-rauc-backend"

FAILED=0

ok() {
    printf 'OK: %s\n' "$1"
}

warn() {
    printf 'BLOCKED: %s\n' "$1"
    FAILED=1
}

echo "=== SECUREEDGE PHASE 11 PREFLIGHT ==="

if [ -s "$BUNDLE" ]; then
    ok "Bundle found"
else
    warn "Complete bundle not found"
fi

if [ -s "$CA" ]; then
    ok "RAUC CA found"
else
    warn "RAUC trust anchor missing"
fi

if command -v rauc >/dev/null 2>&1 &&
   [ -s "$BUNDLE" ] && [ -s "$CA" ]; then
    INFO="$(rauc info --keyring="$CA" "$BUNDLE" 2>&1)"
    STATUS=$?

    if [ "$STATUS" -eq 0 ]; then
        ok "RAUC cryptographic verification"
        printf '%s\n' "$INFO"

        printf '%s\n' "$INFO" |
            grep -Fq 'secureedge-rpi-zero2w' ||
            warn "Compatible string not confirmed"

        printf '%s\n' "$INFO" |
            grep -Fq 'rootfs.ext4' ||
            warn "ROOTFS image not confirmed in manifest"

        printf '%s\n' "$INFO" |
            grep -Fq 'boot.vfat' ||
            warn "BOOT image not confirmed in manifest"
    else
        warn "RAUC signature verification failed"
        printf '%s\n' "$INFO"
    fi
else
    warn "RAUC command or required files unavailable"
fi

if [ -f "$BACKEND" ] && sh -n "$BACKEND"; then
    ok "Backend shell syntax"
else
    warn "Backend missing or invalid"
fi

if [ -f "$BACKEND" ] &&
   grep -Fq 'set-primary disabled outside simulation' "$BACKEND"; then
    warn "Hardware set-primary still disabled"
else
    warn "Hardware boot transaction needs independent audit"
fi

echo
echo "=== FINAL RESULT ==="

if [ "$FAILED" -eq 0 ]; then
    echo "PREFLIGHT BASIC CHECKS PASSED"
else
    echo "PREFLIGHT HAS BLOCKERS"
fi

echo "NO DEVICE WRITES"
echo "NO RAUC INSTALL"
echo "NO REBOOT"

exit 0
