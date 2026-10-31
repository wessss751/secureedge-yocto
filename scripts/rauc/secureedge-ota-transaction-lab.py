#!/usr/bin/env python3
"""Offline RAUC A/B transaction state machine. No hardware operations."""

import argparse
import fcntl
import json
import os
import tempfile
from pathlib import Path

STATES = {
    "STABLE",
    "INSTALLED",
    "TRIAL_ARMED",
    "TRIAL_VERIFIED",
    "COMMITTED",
    "ABORTED",
}

TRANSITIONS = {
    ("STABLE", "installed"): "INSTALLED",
    ("INSTALLED", "arm-trial"): "TRIAL_ARMED",
    ("TRIAL_ARMED", "verified-boot"): "TRIAL_VERIFIED",
    ("TRIAL_VERIFIED", "commit"): "COMMITTED",
    ("INSTALLED", "abort"): "ABORTED",
    ("TRIAL_ARMED", "abort"): "ABORTED",
    ("TRIAL_VERIFIED", "abort"): "ABORTED",
}

def fail(message):
    raise SystemExit("BLOCKED: " + message)

def write_atomic(path, obj):
    fd, temporary = tempfile.mkstemp(
        prefix=".secureedge-", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(obj, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary, path)

        directory = os.open(
            path.parent, os.O_RDONLY | os.O_DIRECTORY
        )
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab-root", required=True)
    parser.add_argument(
        "--action",
        required=True,
        choices=("init", "installed", "arm-trial",
                 "verified-boot", "commit", "abort", "status"),
    )
    parser.add_argument(
        "--primary",
        choices=("system0", "system1"),
    )
    parser.add_argument(
        "--candidate",
        choices=("system0", "system1"),
    )
    args = parser.parse_args()

    root = Path(args.lab_root).absolute()

    if root.is_symlink():
        fail("Symlink laboratory root refused")

    # Lab work is forbidden against production filesystem locations.
    resolved = root.resolve()
    if resolved in (
        Path("/"), Path("/bootctl"), Path("/data"),
        Path("/etc/rauc"),
    ):
        fail("Unsafe laboratory path")

    marker = root / ".secureedge-offline-lab"
    if not marker.is_file() or marker.is_symlink():
        fail("Laboratory marker missing")

    state_file = root / "transaction.json"
    lock_file = root / ".transaction.lock"

    if state_file.is_symlink() or lock_file.is_symlink():
        fail("Transaction symlink refused")

    with open(lock_file, "a+b") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)

        if args.action == "init":
            if state_file.exists():
                fail("Existing transaction")

            primary = args.primary
            candidate = args.candidate

            if not primary or not candidate or primary == candidate:
                fail("Distinct primary and candidate required")

            state = {
                "schema": 1,
                "mode": "offline-lab",
                "primary": primary,
                "candidate": candidate,
                "state": "STABLE",
                "events": [],
            }
            write_atomic(state_file, state)

        else:
            if not state_file.is_file():
                fail("Transaction missing")

            state = json.loads(state_file.read_text())

            if (
                state.get("schema") != 1
                or state.get("mode") != "offline-lab"
                or state.get("state") not in STATES
                or state.get("primary") not in ("system0", "system1")
                or state.get("candidate") not in ("system0", "system1")
                or state["primary"] == state["candidate"]
                or not isinstance(state.get("events"), list)
            ):
                fail("Invalid transaction metadata")

            if args.action != "status":
                old = state["state"]
                key = (old, args.action)
                new = TRANSITIONS.get(key)

                if new is None:
                    fail(f"Forbidden transition: {old} -> {args.action}")

                state["events"].append({
                    "action": args.action,
                    "from": old,
                    "to": new,
                })
                state["state"] = new

                write_atomic(state_file, state)

        print(f'TRANSACTION_STATE={state["state"]}')
        print(f'PRIMARY={state["primary"]}')
        print(f'CANDIDATE={state["candidate"]}')
        print("MODE=offline-lab")
        print("REAL_BOOTCTL_WRITES=NO")
        print("REAL_REBOOT=NO")

if __name__ == "__main__":
    main()
