#!/bin/sh
set -eu

fail() {
    printf 'SECUREEDGE HEALTH FAIL: %s\n' "$*" >&2
    exit 1
}

[ "$#" -eq 1 ] || fail "Usage: $0 BACKEND"

BACKEND="$1"

[ "${SECUREEDGE_TEST_MODE:-0}" != "1" ] ||
    fail "Simulation mode not permitted for hardware health proof"

[ -x "$BACKEND" ] || fail "RAUC backend unavailable"

CURRENT="$( "$BACKEND" get-current )" ||
    fail "Cannot determine current slot"

case "$CURRENT" in
    system0|system1) ;;
    *) fail "Unknown current slot" ;;
esac

VERIFIED="$( "$BACKEND" verify-tryboot )" ||
    fail "Firmware tryboot verification failed"

[ "$VERIFIED" = "verified-tryboot=$CURRENT" ] ||
    fail "Firmware proof does not match current slot"

systemctl is-active --quiet secureedge-agent.service ||
    fail "SecureEdge agent inactive"

WATCHDOG="$(systemctl show -p RuntimeWatchdogUSec --value)" ||
    fail "Cannot read watchdog"

[ "$WATCHDOG" = "10s" ] ||
    fail "Watchdog configuration mismatch"

echo "HEALTH_GATE=PASS"
echo "BOOTED_SLOT=$CURRENT"
echo "TRYBOOT_VERIFIED=1"
echo "AGENT_ACTIVE=1"
echo "WATCHDOG=10s"
