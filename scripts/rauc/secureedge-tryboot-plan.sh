#!/bin/sh
set -eu

fail() {
    printf 'TRYBOOT ERROR: %s\n' "$*" >&2
    exit 1
}

[ "${SECUREEDGE_TEST_MODE:-0}" = "1" ] ||
    fail "Simulation mode required"

[ "$#" -eq 1 ] ||
    fail "Usage: secureedge-tryboot-plan.sh BACKEND"

BACKEND="$1"

[ -f "$BACKEND" ] || fail "Backend not found"
[ -n "${SECUREEDGE_STATE_DIR:-}" ] ||
    fail "Simulation state directory required"

case "$SECUREEDGE_STATE_DIR" in
    /data|/data/*|/bootctl|/bootctl/*)
        fail "Real storage forbidden"
        ;;
esac

PRIMARY="$(sh "$BACKEND" get-primary)" ||
    fail "Cannot determine primary slot"

TRIAL="$(sh "$BACKEND" get-tryboot-target)" ||
    fail "Cannot determine tryboot target"

CURRENT="$(sh "$BACKEND" get-current)" ||
    fail "Cannot determine current slot"

STATE="$(sh "$BACKEND" get-state "$PRIMARY")" ||
    fail "Cannot read recovery slot state"

PENDING_FILE="$SECUREEDGE_STATE_DIR/pending-slot"

[ -f "$PENDING_FILE" ] && [ ! -L "$PENDING_FILE" ] ||
    fail "Pending slot missing or invalid"

PENDING="$(cat "$PENDING_FILE")" ||
    fail "Cannot read pending slot"

[ "$PRIMARY" = "$CURRENT" ] ||
    fail "Not running the normal primary slot"

[ "$PRIMARY" != "$TRIAL" ] ||
    fail "Primary and trial slots are identical"

[ "$PENDING" = "$TRIAL" ] ||
    fail "Pending target does not match tryboot target"

[ "$STATE" = "good" ] ||
    fail "Recovery slot is not good"

printf 'PRIMARY=%s\n' "$PRIMARY"
printf 'CURRENT=%s\n' "$CURRENT"
printf 'TRIAL=%s\n' "$TRIAL"
printf 'PENDING=%s\n' "$PENDING"
printf 'RECOVERY_STATE=%s\n' "$STATE"
printf 'RESULT=READY_FOR_TRYBOOT_SIMULATION\n'
printf 'PLANNED_REBOOT_ARGUMENT=0 tryboot\n'
printf 'NO_REBOOT_EXECUTED\n'
