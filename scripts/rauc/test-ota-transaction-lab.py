#!/usr/bin/env python3
"""Integrated offline transaction state-machine tests."""

import json
import subprocess
import tempfile
from pathlib import Path

TOOL = Path(__file__).with_name(
    "secureedge-ota-transaction-lab.py"
).resolve()

def run(root, action, primary=None, candidate=None):
    command = [
        "python3", str(TOOL),
        "--lab-root", str(root),
        "--action", action,
    ]
    if primary:
        command += ["--primary", primary]
    if candidate:
        command += ["--candidate", candidate]

    return subprocess.run(
        command, text=True, capture_output=True
    )

def setup(primary="system0", candidate="system1"):
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    (root / ".secureedge-offline-lab").touch()

    result = run(root, "init", primary, candidate)
    assert result.returncode == 0, result.stderr

    return temp, root

def state(root):
    return json.loads(
        (root / "transaction.json").read_text()
    )["state"]

# 1. Nominal A -> B
tmp, root = setup()
for action, expected in (
    ("installed", "INSTALLED"),
    ("arm-trial", "TRIAL_ARMED"),
    ("verified-boot", "TRIAL_VERIFIED"),
    ("commit", "COMMITTED"),
):
    assert run(root, action).returncode == 0
    assert state(root) == expected
print("PASS: nominal A -> B")
tmp.cleanup()

# 2. Nominal B -> A
tmp, root = setup("system1", "system0")
for action in (
    "installed", "arm-trial", "verified-boot", "commit"
):
    assert run(root, action).returncode == 0
assert state(root) == "COMMITTED"
print("PASS: nominal B -> A")
tmp.cleanup()

# 3. Reject premature confirmation
tmp, root = setup()
assert run(root, "commit").returncode != 0
assert state(root) == "STABLE"
print("PASS: premature commit rejected")
tmp.cleanup()

# 4. Abort before trial
tmp, root = setup()
assert run(root, "installed").returncode == 0
assert run(root, "abort").returncode == 0
assert state(root) == "ABORTED"
assert run(root, "commit").returncode != 0
print("PASS: aborted candidate cannot be committed")
tmp.cleanup()

# 5. Abort after trial preparation
tmp, root = setup()
assert run(root, "installed").returncode == 0
assert run(root, "arm-trial").returncode == 0
assert run(root, "abort").returncode == 0
assert state(root) == "ABORTED"
print("PASS: trial failure blocks promotion")
tmp.cleanup()

# 6. Reject duplicate initialization
tmp, root = setup()
assert run(
    root, "init", "system0", "system1"
).returncode != 0
assert state(root) == "STABLE"
print("PASS: duplicate transaction rejected")
tmp.cleanup()

print("PHASE_11_TRANSACTION_LAB=PASS")
print("HARDWARE_OTA=NO-GO")
