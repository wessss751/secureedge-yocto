#!/usr/bin/env python3
"""Offline model of SecureEdge A/B trial boot and confirmation."""

import json
from pathlib import Path

SLOTS = ("system0", "system1")


class BootError(Exception):
    pass


class ABModel:
    def __init__(self):
        self.primary = "system0"
        self.booted = "system0"
        self.pending = None
        self.trial = False
        self.health_passed = False
        self.states = {"system0": "good", "system1": "bad"}

    def prepare(self, slot):
        if slot not in SLOTS or slot == self.primary:
            raise BootError("Target must be inactive slot")
        if self.pending is not None:
            raise BootError("Trial already pending")

        self.pending = slot
        self.states[slot] = "bad"
        self.health_passed = False

    def tryboot(self):
        if self.pending is None or self.trial:
            raise BootError("No pending trial")

        self.booted = self.pending
        self.trial = True
        self.health_passed = False

    def check_health(self, healthy):
        if not self.trial or self.booted != self.pending:
            raise BootError("Not running a trial slot")

        self.health_passed = bool(healthy)
        return self.health_passed

    def confirm(self):
        if not self.trial or self.booted != self.pending:
            raise BootError("No matching trial boot")
        if not self.health_passed:
            raise BootError("Health verification missing or failed")

        self.states[self.booted] = "good"
        self.primary = self.booted
        self.pending = None
        self.trial = False
        self.health_passed = False

    def normal_reboot(self):
        """Simulate firmware one-shot tryboot flag being cleared."""
        if self.trial and self.pending is not None:
            self.states[self.pending] = "bad"

        self.booted = self.primary
        self.pending = None
        self.trial = False
        self.health_passed = False

    def snapshot(self):
        return {
            "primary": self.primary,
            "booted": self.booted,
            "pending": self.pending,
            "trial": self.trial,
            "health_passed": self.health_passed,
            "states": dict(self.states),
        }


def demo():
    model = ABModel()

    def show(stage):
        print(f"\n=== {stage} ===")
        print(json.dumps(model.snapshot(), indent=2))

    show("Initial: stable A")
    model.prepare("system1")
    show("B prepared")
    model.tryboot()
    show("Trial boot B")
    model.check_health(True)
    model.confirm()
    show("B confirmed")

    model.prepare("system0")
    model.tryboot()
    model.check_health(False)
    show("Trial A failed")
    model.normal_reboot()
    show("Rollback to stable B")


if __name__ == "__main__":
    demo()
