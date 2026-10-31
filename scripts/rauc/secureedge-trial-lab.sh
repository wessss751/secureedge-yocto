#!/bin/sh
set -eu

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

[ "$#" -eq 1 ] || fail "Usage: $0 BACKEND"

BACKEND="$1"

[ "${SECUREEDGE_TEST_MODE:-0}" = "1" ] ||
    fail "Simulation required"

[ -n "${SECUREEDGE_BOOTCTL_DIR:-}" ] ||
    fail "BOOTCTL fixture required"

[ -n "${SECUREEDGE_STATE_DIR:-}" ] ||
    fail "State fixture required"

[ -n "${SECUREEDGE_CMDLINE_FILE:-}" ] ||
    fail "Cmdline fixture required"

for path in \
    "$SECUREEDGE_BOOTCTL_DIR" \
    "$SECUREEDGE_STATE_DIR" \
    "$SECUREEDGE_CMDLINE_FILE"
do
    case "$path" in
        /bootctl|/bootctl/*|/data|/data/*|/proc|/proc/*|/dev|/dev/*)
            fail "Real hardware path forbidden"
            ;;
    esac
done

PRIMARY="$(sh "$BACKEND" get-primary)"
CURRENT="$(sh "$BACKEND" get-current)"
TRIAL="$(sh "$BACKEND" get-tryboot-target)"

[ "$PRIMARY" = "$CURRENT" ] ||
    fail "Current slot is not the primary"

[ "$PRIMARY" != "$TRIAL" ] ||
    fail "Trial slot equals primary"

[ "$(sh "$BACKEND" get-state "$PRIMARY")" = "good" ] ||
    fail "Recovery slot is not good"

PENDING="$SECUREEDGE_STATE_DIR/pending-slot"

[ -f "$PENDING" ] && [ ! -L "$PENDING" ] ||
    fail "No pending transaction"

[ "$(cat "$PENDING")" = "$TRIAL" ] ||
    fail "Pending transaction mismatch"

echo "PRIMARY=$PRIMARY"
echo "TRIAL=$TRIAL"
echo "RECOVERY=good"
echo "RESULT=READY_FOR_TRYBOOT"
echo "ACTION=LAB_ONLY"
