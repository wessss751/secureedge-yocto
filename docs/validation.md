# Validation record

Status reviewed on 2026-11-02. Reported hardware observations, archived records and source inspection are distinct evidence categories. Code and checklists describe behavior or requirements; they do not prove execution.

## Reported Raspberry Pi Zero 2 W observations

| Observation | Repository corroboration | Raw evidence archived in Git |
| --- | --- | --- |
| Slot A boot: ROOTFS_A, `rauc.slot=system0` | [Phase 9](rauc/phase9-final-validation.md) reports A operation; tracked command line maps A to system0 | No corresponding command-line or firmware capture |
| SecureEdge Agent active | Phase 9 reports agent operation | No recent service log or telemetry capture |
| Signed SecureEdge bundle verification observed | Signing/verification implementation exists | No verification transcript for the reported 10.2 bundle |
| SecureEdge `10.2-ab-evidence-lab` bundle installed using RAUC on B | Local experimental recipe describes boot/rootfs slots and bundle version | No RAUC completion log; the local recipe is untracked |
| B image integrity verification performed | Signed-target checker exists; local payload recipe specifies expected hashes/sizes | No captured post-install audit result |
| Activation arm service completed successfully (`secureedge-rauc-activation --arm`) | Tracked executable implements explicit arming separately from reboot | No arming invocation or service log |
| Persistent `trial_armed` state verified | Activation writes this state after its signed-target audit | No sanitized device transaction record |

These observations were reported by the project owner and were not rerun for this record. The bundle identifier is not the RAUC executable version; the version running on the device is not established here.

**First actual boot on B and complete automatic rollback qualification remain pending.** Arming alone proves neither. Historical Phase 9 notes also report MQTT mTLS, watchdog configuration, partition layout and restricted access; watchdog configuration is not proof of watchdog-triggered recovery.

## Archived host-side records

- [Phase 9](rauc/phase9-final-validation.md) records laboratory backend, slot-reading, trial-preparation and BOOTCTL confirmation simulations as narrative results.
- The [offline readiness report](rauc/evidence/phase11-readiness.json), generated on 2026-10-31, records PASS entries for its artifact, layout and syntax checks. Its scope is `offline-readiness`, hardware status is `NO-GO`, and it records no device writes. External inputs have not been rechecked.
- `tests/rauc/` contains backend, layout, confirmation, health, watchdog and rollback contracts/simulations. A current full-suite execution report is not archived in Git.
- The application Makefile defines sensor and configuration tests. They do not cover the separate recipe-side MQTT implementation.

The [Phase 10](rauc/phase10-signed-bundle.md) and [Phase 11 acceptance](rauc/phase11-final-acceptance.md) checklists retain their original milestone state. Earlier statements that installation had not occurred precede the later reported observations; unchecked entries are not converted into successful test results.

## Source inspection findings

- Base Pi/QEMU profiles omit `meta-rauc` while platform metadata requires its class and recipes. This is a static parsing blocker, not an executed build failure.
- Orchestrated health emits `MQTT_MTLS_VERIFIED=NO`; `--confirm-check` deliberately blocks. Laboratory confirmation relies on operator-reviewed telemetry.
- The standalone orchestrated profile does not select the watchdog package required by its health check. Service-monitor installation/enablement is also not automatic.
- The tracked `10.1-ab-lab` bundle is rootfs-only; local 10.2 boot/rootfs payloads are not reproducible from a fresh checkout.

## Documentation checks

The 2026-11-02 audit parsed 34 Python files without execution and scanned working files and 208 historical blobs for selected secret signatures. No matching private-key, AWS access-ID or GitHub-token signature was detected. Later documentation checks validated local Markdown links, whitespace and selected sensitive patterns. These checks do not establish functional correctness or exhaustive secret clearance.

No Yocto/Kas build, C test, RAUC functional test or hardware operation was executed for these documentation revisions. ShellCheck, Gitleaks and Kas were unavailable in the inspected host PATH. Build examples remain unexecuted.

## Required acceptance evidence

Archive sanitized records of Git revision, resolved inputs, artifact hashes, board identity, operator/time, exit status and relevant logs. Include signed-bundle verification, installation completion, installed-image audit and persistent arming state; exclude credentials and private keys.

Next hardware evidence must establish B firmware tryboot identity, ROOTFS_B/system1 agreement, agent/mTLS health, durable confirmation, subsequent normal B reboot and failed-candidate rollback to A. Power-loss and watchdog recovery require separate fault qualification. Use the [acceptance checklist](rauc/phase11-final-acceptance.md) as the detailed engineering gate.
