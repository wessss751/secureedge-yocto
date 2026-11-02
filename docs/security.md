# Security architecture

## Trust boundaries

Device identity, update-signing authority, the unprivileged telemetry service and privileged update operations have separate roles. MQTT mutual TLS authenticates the device/broker connection when correctly provisioned. RAUC signatures authenticate bundle contents against the configured trust anchor. Hardware-rooted secure boot is not implemented.

## Production service isolation

The [PROD systemd drop-in](../meta-secureedge-platform/recipes-security/secureedge-hardening/files/30-prod-hardening.conf) runs the agent as `secureedge`, removes capabilities, enables `NoNewPrivileges`, restricts filesystem access and isolates temporary files. Startup requires the TLS switch. The PROD image removes inherited development login features.

The maintenance account has a limited passwordless sudo command set for agent restart and recent journal access. Device credentials, service configuration and administrative provisioning remain part of the deployment trust boundary.

Watchdog and service-monitor recipes do not establish runtime protection merely by existing. Their profile selection and enablement are described in [architecture](architecture.md#runtime-integration).

## MQTT mutual TLS and persistent identity

The recipe-side client passes CA, device-certificate and private-key paths to libmosquitto; server certificate and hostname verification remain enabled. The [example environment file](../scripts/examples/mqtt-tls.env.example) contains paths rather than key material. DEV can operate without TLS; PROD requires `SECUREEDGE_MQTT_TLS=1` through its service policy.

The baseline environment is `/etc/secureedge/mqtt-tls.env`. Only the orchestrated profile selects the persistent override using `/data/secureedge/identity/mqtt-tls.env` and `/data/secureedge/config/agent.conf`, with mount and initialization dependencies. Provision the candidate's identity before health acceptance.

Keep private keys and live credentials outside Git. Signing-key custody, device-certificate rotation, revocation and expiry handling require a deployment policy.

## Implemented update checks

Signed RAUC bundle verification and signed-target integrity checking are implemented. The repository contains a public development CA; it is not a production trust-anchor policy. The `verity` bundle format does not establish runtime dm-verity protection of the root filesystem.

The orchestrated profile disables automatic activation. Its installation service is not automatically enabled. Explicit arming checks A identity, the protected candidate, installation state and signed-target audit before recording `trial_armed`; it neither reboots nor writes BOOTCTL.

## Confirmation boundaries

| Mechanism | Current guarantee and limit |
| --- | --- |
| Orchestrated health tool | Checks B boot identity, agent activity and watchdog configuration; explicitly reports `MQTT_MTLS_VERIFIED=NO` |
| Activation `--confirm-check` | Intentionally blocks confirmation: broker-side mTLS delivery is not verified and FAT recovery is unqualified |
| Separate laboratory confirmer | Requires explicit approvals and operator-reviewed telemetry evidence bound to the candidate; this is a human attestation, not authenticated broker-side proof |
| FAT BOOTCTL update | Laboratory tooling exists, but power-loss recovery and atomicity are not qualified |

An active agent or a successful local health result does not prove authenticated telemetry reached the broker. There is no automated end-to-end broker-side mTLS health guarantee in the orchestrated workflow.

## Pending qualification

First B boot, durable confirmation, complete automatic rollback, interrupted FAT writes and watchdog/power-loss recovery require hardware acceptance. Retain a known-good recovery slot until qualified. No SELinux enforcement, OP-TEE integration, dm-crypt encryption or runtime dm-verity deployment is claimed.

See [validation](validation.md) for the evidence boundary and [roadmap](roadmap.md) for remaining work.
