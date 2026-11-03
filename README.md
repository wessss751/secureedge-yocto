# SecureEdge Yocto

SecureEdge is an Embedded Linux project for Raspberry Pi Zero 2 W using Yocto Project Scarthgap. It combines a C telemetry agent, systemd service hardening, MQTT over mutual TLS and signed RAUC updates with separate A/B boot and root filesystem partitions. QEMU ARM64 is included as a development configuration.

## Features

- Custom platform and distribution layers with Kas build profiles.
- C agent using libmosquitto to publish synthetic temperature and voltage readings on per-device topics.
- PROD service isolation, a dedicated service identity and restricted maintenance access.
- Device-local mTLS provisioning; the orchestrated profile selects persistent identity and configuration on DATA.
- Signed verity-format RAUC bundles, inactive-slot integrity checks and explicit trial arming.
- Raspberry Pi tryboot tooling and host-side boot/transaction simulations.

## Architecture

```text
C telemetry agent ── MQTT / mutual TLS ── broker
        └── systemd service isolation (PROD)

Signed bundle → RAUC verification/install → inactive B images
                                                 │
                                        integrity verification
                                                 │
                                         explicit trial arming
                                                 │
                               B boot / confirmation / rollback
                                    (qualification pending)

Storage: BOOTCTL | BOOT_A | BOOT_B | ROOTFS_A | ROOTFS_B | DATA
```

Watchdog and service-monitor components are available in the source tree; installation and enablement depend on the profile. See [runtime integration](docs/architecture.md#runtime-integration).

## Project status

Reported hardware results include slot A boot (`ROOTFS_A`, `system0`), an active agent, signed bundle verification, and the SecureEdge `10.2-ab-evidence-lab` bundle installed using RAUC on B. B image integrity checks, successful `secureedge-rauc-activation --arm` execution and persistent `trial_armed` state were also reported.

Host regression checks passed: 128 RAUC cases, six offline transaction cases and two C test programs. Optimized-Python and import/syntax checks also passed.

**First boot on B and complete automatic rollback qualification remain pending.** The [validation record](docs/validation.md) separates reported observations from archived evidence. Hardware-rooted secure boot and automated broker-side mTLS health verification are not implemented.

## Reproduction and documentation

The [build guide](docs/build.md) records the pinned layer dependencies, resolved profiles and recipe-parsing results. The unchanged Dockerfile was built and checked with UID/GID `1000:1000`; no full Yocto image build is claimed. The tracked bundle configuration is rootfs-only `10.1-ab-lab`. The experimental `10.2-ab-evidence-lab` recipe and payloads are retained outside the curated public source tree.

| Document | Contents |
| --- | --- |
| [Architecture](docs/architecture.md) | Runtime integration, A/B partitions and update stages |
| [Build](docs/build.md) | Container prerequisites, profile dependencies and reproducibility limits |
| [Security](docs/security.md) | Hardening, mTLS, signing and confirmation boundaries |
| [Validation](docs/validation.md) | Hardware observations, host evidence and acceptance gaps |
| [Roadmap](docs/roadmap.md) | Remaining integration and qualification work |

## Repository layout

- `application/secureedge-agent/`: application sources and C unit tests.
- `meta-secureedge-platform/`: platform, application, security and RAUC integration.
- `meta-secureedge-distro/`: distribution configuration.
- `kas/` and `docker/`: build profiles and container definition.
- `scripts/` and `tests/rauc/`: provisioning tools, laboratory procedures and host tests.
- `docs/rauc/`: historical engineering records and acceptance plans.

`secureedge-prod-v1` preserves the production baseline; `feat/rauc-ab` preserves RAUC development. Builds, caches and external layer checkouts are excluded from Git.

## Licensing

Original SecureEdge-owned source, scripts, tests, configuration and documentation
are licensed under the [MIT License](LICENSE).
Copyright (c) 2026 wissem

This grant applies to original SecureEdge-owned material only. Third-party
components, dependencies, firmware and any material carrying separate notices
remain subject to their respective licenses and redistribution requirements;
the root license does not relicense them. Existing [platform](meta-secureedge-platform/COPYING.MIT)
and [distribution](meta-secureedge-distro/COPYING.MIT) MIT notices are preserved
unchanged. External Yocto layers and their payloads retain their own licenses;
firmware license acceptance does not establish redistribution permission.

**Recipe metadata remains inconsistent with this licensing decision:** 16 recipes
still declare `LICENSE = "CLOSED"`. Those declarations are unchanged. A separate
review must establish each recipe's source and payload ownership, applicable
licenses, third-party obligations and required Yocto license/checksum metadata
before updating those declarations or claiming complete license alignment.

GitHub publication requires separate owner approval and is not authorized by
this licensing decision.
