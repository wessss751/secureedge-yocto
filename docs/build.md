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

The platform metadata requires meta-rauc even for baseline images: the bundle recipe inherits `bundle`, and RAUC appends need matching recipes. Both base profiles now supply the layer. All profiles pin meta-rauc to `d63878f20eba7a85ecf53566e7a3377e78bb46ac`, verified against upstream Scarthgap HEAD during release preparation.

No RAUC package, service or runtime feature was added to baseline image declarations. The existing RAUC profiles retain their feature selection. The platform layer's declared `core` dependency alone does not describe this metadata requirement.

Kas 4.8 resolved all six profiles with the pinned revision. The following `bitbake -p` checks completed with zero errors:

| Profile | Recipe parsing |
| --- | --- |
| `kas/qemu.yml` | Passed (2,732 recipes) |
| `kas/rpi-zero2.yml` | Passed (2,779 recipes) |
| `kas/rpi-zero2-rauc.yml` | Passed (2,779 recipes) |
| `kas/rpi-zero2-rauc-custom-test.yml` | Passed (2,779 recipes) |
| `kas/rpi-zero2-rauc-orchestrated.yml` | Passed (2,779 recipes) |
| `kas/rpi-zero2-watchdog-test.yml` | Passed (2,779 recipes) |

Expanded metadata confirmed that baseline QEMU DEV and Pi PROD targets do not select RAUC packages/features, and that PROD insecure-login features remain removed.

Validation used an independently built container from the unchanged Dockerfile, isolated build directories and pre-existing source caches at the configured revisions. This is configuration/parsing evidence, not a clean image build or runtime qualification. Baseline profiles warn that the RAUC distro feature is disabled; this is intentional. The configuration-only distro layer also produces a no-recipes warning.

## Container prerequisites and parsing commands

Use a Linux host with Docker, network access and sufficient storage for Yocto builds and caches. Run BitBake as a non-root user. Before building, ensure:

- The container account resolves the selected UID/GID through its user/group databases. Numeric Docker `--user` arguments alone do not create an account.
- The account can write the checkout, build directory, download cache and shared-state cache, and has a writable HOME.
- The checkout is mounted at `/workspace`; host permissions match the selected UID/GID.

The unchanged Dockerfile built successfully and passed account lookup, HOME/cache write and Kas startup checks with UID/GID `1000:1000` and `HOME=/tmp`. No Dockerfile correction was needed for that environment. Arbitrary UID/GID mappings remain unverified; check the prerequisites above on other hosts.

The container definition needs no repository build context because it contains no COPY or ADD instructions:

```sh
docker build -t secureedge-build - < docker/Dockerfile
```

The following runs recipe parsing for the validated orchestrated profile. It uses default Kas checkout/build paths; validation used isolated directories and cached sources instead. Fresh source fetching and image construction have not been qualified. The extra read-only Git metadata mount supports linked worktrees:

```sh
secureedge_git_common="$(git rev-parse --path-format=absolute --git-common-dir)"
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -v "$PWD:/workspace" \
  -v "$secureedge_git_common:$secureedge_git_common:ro" \
  -w /workspace \
  secureedge-build \
  kas shell -c 'bitbake -p' kas/rpi-zero2-rauc-orchestrated.yml
```

Kas 4.8 supports the configuration formats used here, including versions 14 and 19. Includes are repository-relative; its file-relative fallback supports the sibling-file includes with a deprecation warning. The base RAUC include `kas/rpi-zero2.yml` is repository-relative. Mixed header versions alone do not establish a parsing defect. These rules are documented in the [Kas format history](https://kas.readthedocs.io/en/4.8/format-changelog.html).

With default Kas paths, images are under `build/tmp/deploy/images/<machine>/`; downloads and shared state are configured under `/workspace/.kas/`. Use separate build directories for different profiles. No flashing, provisioning, installation or reboot procedure is included here.

## Bundles and signing

The tracked [bundle recipe](../meta-secureedge-platform/recipes-core/bundles/secureedge-bundle-ab.bb) declares `10.1-ab-lab`, uses `verity` and builds only the rootfs slot. Boot-image generation remains unfinished in that recipe.

The SecureEdge `10.2-ab-evidence-lab` bundle installed using RAUC is a reported hardware result. Its experimental recipe and boot/rootfs payloads are retained outside this curated public source tree. They are not supplied by a fresh checkout and are not a reproducible replacement for the tracked 10.1 configuration. Bundle versions do not identify the RAUC executable version, which is not established by the available hardware evidence.

Signing requires private local configuration for `RAUC_KEY_FILE`, `RAUC_CERT_FILE` and, where required by the bundle class, `RAUC_KEYRING_FILE`. Keep signing keys outside Git and public build inputs, with restricted access. The public trust anchor must match the signing identity.

## Reproducibility limits

- Poky, meta-openembedded, meta-raspberrypi and meta-rauc are commit-pinned. Source pins do not establish bit-for-bit image reproducibility.
- The container uses a mutable Ubuntu tag and live package repositories; pinning Kas does not freeze the complete build environment.
- The application tree and recipe payload differ. Host application tests do not cover all image-side MQTT code.
- Watchdog and monitor installation/enablement need explicit profile integration; see [runtime integration](architecture.md#runtime-integration).
- Firmware license acceptance remains applicable; the Pi profile accepts the configured Synaptics firmware flag for laboratory use.

A full image build remains to be verified. After parsing, the PROD build target is selected with `kas build --target secureedge-image-rpi-prod kas/rpi-zero2-rauc-orchestrated.yml`; that image-build command was not executed during these checks. Record resolved revisions, artifact hashes and results in [validation](validation.md).
