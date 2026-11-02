# SecureEdge architecture

## Build structure

SecureEdge uses Yocto Project Scarthgap. The [distribution layer](../meta-secureedge-distro/README) selects systemd, usrmerge and the distribution identity. The [platform layer](../meta-secureedge-platform/README) contains image recipes, the agent, networking, storage, security policies and RAUC integration.

Kas selects `qemuarm64` or `raspberrypi0-2w-64`. Raspberry Pi Zero 2 W is the hardware target; QEMU does not reproduce its firmware or watchdog behavior. The base profiles include pinned meta-rauc metadata required by the platform layer; see [build dependencies](build.md#current-parsing-dependency).

## Runtime integration

| Component | Selection and enablement in source |
| --- | --- |
| SecureEdge Agent | Included by the development image inherited by Pi DEV/PROD; its service is enabled |
| PROD agent hardening | Added by `secureedge-image-rpi-prod`; runs the agent as `secureedge` with systemd restrictions and mandatory TLS configuration |
| Persistent identity/configuration | Selected by `SECUREEDGE_RAUC_ORCHESTRATED=1`; installs the agent DATA override |
| DATA mount and initialization | Selected by the RAUC profile; mount and initialization units are enabled |
| RAUC healthcheck service | Selected by the RAUC profile; disabled by default |
| Installation coordinator and activation tools | Added to the PROD image in the orchestrated profile; installation service is disabled by default |
| Hardware watchdog configuration | Explicitly selected by the watchdog test profile; the standalone orchestrated profile does not select this package |
| Critical service monitor | Recipe exists; no inspected image/profile selects it and its service is disabled by default |

These are metadata selections, not a verified runtime inventory. In particular, the orchestrated health tool expects a 10-second watchdog configuration that its standalone profile does not supply. Candidate-image integration must resolve this prerequisite before health acceptance.

The agent publishes synthetic temperature and voltage readings through libmosquitto. The application tree and recipe payload differ in MQTT implementation and default configuration; the image compiles the recipe payload. The orchestrated profile selects `/data/secureedge/config/agent.conf` and `/data/secureedge/identity/mqtt-tls.env`. Other A/B profiles do not automatically select this persistent identity override.

## A/B partition layout

[secureedge-rauc-ab.wks](../meta-secureedge-platform/wic/secureedge-rauc-ab.wks) defines an MBR layout with p4 reserved for the extended partition.

| Partition | Label | Filesystem | Configured size (MiB) | Role |
| --- | --- | --- | --- | --- |
| p1 | BOOTCTL | FAT | 64 | Initial firmware and boot selection |
| p2 | BOOT_A | FAT | 192 | A firmware, kernel and command line |
| p3 | BOOT_B | FAT | 192 | B firmware, kernel and command line |
| p4 | Extended | — | — | Container for logical partitions |
| p5 | ROOTFS_A | ext4 | 512 | A root filesystem, system0 |
| p6 | ROOTFS_B | ext4 | 512 | B root filesystem, system1 |
| p7 | DATA | ext4 | 1024 | Persistent configuration, identity and update state |

A maps BOOT_A to ROOTFS_A with `rauc.slot=system0`; B maps BOOT_B to ROOTFS_B with `rauc.slot=system1`. These configured mappings require matching firmware and live root filesystem evidence before accepting a boot.

DATA is mounted at `/data` with `nosuid,nodev`. Initialization checks the mount and rejects symlink redirection. RAUC state and transaction records live under `/data/rauc` and `/data/secureedge-rauc`.

## Update stages

| Stage | Current implementation |
| --- | --- |
| Verify and install | RAUC verifies the signed bundle; a guarded installation path targets inactive B |
| Audit installed images | Signed-target tooling checks B against the candidate bundle |
| Arm | Explicit activation records `trial_armed`; no reboot or BOOTCTL write |
| Dispatch trial | Tooling requests one-shot tryboot; first actual B boot remains unvalidated |
| Check health | Checks firmware/rootfs identity, agent activity and watchdog configuration; reports `MQTT_MTLS_VERIFIED=NO` |
| Confirm | `--confirm-check` intentionally blocks; a separate laboratory tool requires operator-reviewed telemetry and explicit approvals |
| Qualify recovery | FAT power-loss recovery and complete automatic rollback remain pending |

The [orchestrated configuration](../meta-secureedge-platform/recipes-core/rauc/files/system-orchestrated.conf) uses `bootloader=noop` and `activate-installed=false`. RAUC installation does not implicitly switch boot selection. The custom backend is a separate, mutually exclusive laboratory mode.

See [security](security.md) for confirmation limits and [validation](validation.md) for evidence. The historical [transaction contract](rauc/phase11-transaction-contract.md), [recovery policy](rauc/boot-recovery-policy.md) and [acceptance checklist](rauc/phase11-final-acceptance.md) retain their milestone context.
