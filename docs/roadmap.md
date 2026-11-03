# Roadmap

## Reproducible build inputs

- Maintain pinned layer revisions and repeat configuration resolution/parsing when updating them.
- Reproduce complete boot/rootfs bundles from versioned inputs without external laboratory payload dependencies.
- Verify the container account mapping and a clean build; record source revisions, artifact hashes and host requirements.
- Clarify source ownership between the application tree and recipe payload before consolidation.

## Runtime integration and hardware acceptance

- Integrate and verify watchdog configuration for the orchestrated candidate; explicitly select and enable service monitoring where required.
- Establish broker-side mTLS telemetry evidence rather than inferring it from agent activity.
- Archive verification, B installation, image-audit and `trial_armed` evidence for the reported SecureEdge `10.2-ab-evidence-lab` bundle installed using RAUC.
- Capture the first B boot with matching firmware, root filesystem and slot identity; verify agent operation and persistent identity.
- Validate durable confirmation and subsequent normal B boot.
- Qualify complete automatic rollback, interrupted BOOTCTL writes, power-loss recovery and watchdog recovery.

## Public release decisions

- Review third-party and firmware redistribution obligations for release artifacts. The 16 original SecureEdge recipes now have MIT license/checksum metadata consistent with the [approved MIT scope](../README.md#licensing); this does not establish complete image compliance.
- Obtain separate owner approval before GitHub publication.
- Review local experimental work and identify the versioned inputs required for reproduction.
- Define signing-key custody, trust-anchor and certificate-lifecycle policies.
- Add CI after reviewing host-test isolation and dependencies.
- Review release contents and Git history for secrets and private environment details.

## Longer-term security work

Evaluate hardware-rooted secure boot, runtime integrity, storage encryption and mandatory access controls against a defined threat model. These remain possible extensions, not implemented guarantees.
