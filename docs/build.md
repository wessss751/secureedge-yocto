# Build and reproduction

## Confirmed configuration facts

The repository defines Yocto Project Scarthgap profiles for Raspberry Pi Zero 2 W and QEMU ARM64. The Dockerfile uses Ubuntu 24.04 and installs Kas 4.8 in a virtual environment. Local layer paths require the checkout at `/workspace`.

| Profile | Default image | Configuration |
| --- | --- | --- |
| `kas/qemu.yml` | `secureedge-image-dev` | QEMU ARM64 development |
| `kas/rpi-zero2.yml` | `secureedge-image-rpi-dev` | Pi development |
| `kas/rpi-zero2-rauc.yml` | Inherits Pi DEV | RAUC and A/B WIC layout |
| `kas/rpi-zero2-rauc-custom-test.yml` | Inherits Pi DEV | Laboratory custom boot backend |
| `kas/rpi-zero2-rauc-orchestrated.yml` | Inherits Pi DEV | External update orchestration |
| `kas/rpi-zero2-watchdog-test.yml` | Inherits Pi DEV | Watchdog test settings targeting PROD |

Select `secureedge-image-rpi-prod` explicitly for PROD. Both base profiles enable `debug-tweaks`; the PROD recipe removes inherited development/login features and adds hardening. Device-local network and mTLS provisioning are still required. Custom-backend and orchestrated modes cannot be combined.

## Current parsing dependency

**The base Pi and QEMU build paths are blocked by a dependency identified through static inspection.** They omit `meta-rauc`, while the platform layer discovers the tracked bundle recipe (`inherit bundle`) and the `rauc-conf.bbappend` and `rauc_%.bbappend` files. The class and matching recipes come from `meta-rauc`. No applicable masking or conditional inclusion was found. Choosing a non-RAUC target does not exclude this metadata from parsing.

Consequently, `kas build kas/rpi-zero2.yml`, its PROD target variant and `kas build kas/qemu.yml` are not verified build instructions for the current tree. This is a static finding, not a captured BitBake failure. Fixing layer composition or isolating optional RAUC metadata requires a reviewed configuration change.

RAUC profiles include `meta-rauc`, which addresses this particular missing dependency; their full builds remain unverified. The actual metadata dependency is broader than the platform layer's declared `core` dependency.

## Container prerequisites and unexecuted example

Use a Linux host with Docker, network access and sufficient storage for Yocto builds and caches. Run BitBake as a non-root user. Before building, ensure:

- The container account resolves the selected UID/GID through its user/group databases. Numeric Docker `--user` arguments alone do not create an account.
- The account can write the checkout, build directory, download cache and shared-state cache, and has a writable HOME.
- The checkout is mounted at `/workspace`; host permissions match the selected UID/GID.

The existing Dockerfile does not create a build account matching arbitrary host IDs. Verify the account mapping or provide a separately reviewed container setup before using the example below.

The container definition needs no repository build context because it contains no COPY or ADD instructions:

```sh
docker build -t secureedge-build - < docker/Dockerfile
```

The following is an **unexecuted example** for the orchestrated PROD target, conditional on the prerequisites above. No clean-build validation is available:

```sh
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$PWD:/workspace" \
  -w /workspace \
  secureedge-build \
  kas build kas/rpi-zero2-rauc-orchestrated.yml --target secureedge-image-rpi-prod
```

Kas 4.8 supports the configuration formats used here, including versions 14 and 19. Includes are repository-relative; its file-relative fallback supports the sibling-file includes with a deprecation warning. The base RAUC include `kas/rpi-zero2.yml` is repository-relative. Mixed header versions alone do not establish a parsing defect. These rules are documented in the [Kas format history](https://kas.readthedocs.io/en/4.8/format-changelog.html).

With default Kas paths, images are under `build/tmp/deploy/images/<machine>/`; downloads and shared state are configured under `/workspace/.kas/`. Use separate build directories for different profiles. No flashing, provisioning, installation or reboot procedure is included here.

## Bundles and signing

The tracked [bundle recipe](../meta-secureedge-platform/recipes-core/bundles/secureedge-bundle-ab.bb) declares `10.1-ab-lab`, uses `verity` and builds only the rootfs slot. Boot-image generation remains unfinished in that recipe.

The SecureEdge `10.2-ab-evidence-lab` bundle installed using RAUC is a reported hardware result. Its local experimental recipe supplies boot and rootfs payloads from external laboratory storage, with expected hashes and sizes. The recipe is untracked and its payloads are not supplied by a fresh checkout; it is not a reproducible replacement for the tracked 10.1 configuration. Bundle versions do not identify the RAUC executable version, which is not established by the available hardware evidence.

Signing requires private local configuration for `RAUC_KEY_FILE`, `RAUC_CERT_FILE` and, where required by the bundle class, `RAUC_KEYRING_FILE`. Keep signing keys outside Git and public build inputs, with restricted access. The public trust anchor must match the signing identity.

## Reproducibility limits

- Poky, meta-openembedded and meta-raspberrypi have commit pins; **meta-rauc follows `scarthgap` without a commit pin**.
- The container uses a mutable Ubuntu tag and live package repositories; pinning Kas does not freeze the complete build environment.
- The application tree and recipe payload differ. Host application tests do not cover all image-side MQTT code.
- Watchdog and monitor installation/enablement need explicit profile integration; see [runtime integration](architecture.md#runtime-integration).
- Firmware license acceptance remains applicable; the Pi profile accepts the configured Synaptics firmware flag for laboratory use.

Resolve the base parsing dependency, pin the remaining inputs and verify a clean build before claiming reproducibility. Record resolved revisions, artifact hashes and results in [validation](validation.md).
