
# SecureEdge - Yocto build environment
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    chrpath \
    cpio \
    debianutils \
    diffstat \
    file \
    gawk \
    gcc \
    git \
    iputils-ping \
    libacl1 \
    liblz4-tool \
    locales \
    python3 \
    python3-git \
    python3-jinja2 \
    python3-pexpect \
    python3-pip \
    python3-venv\
    python3-subunit \
    socat \
    texinfo \
    unzip \
    wget \
    xz-utils \
    zstd \
    qemu-system-arm \
    qemu-utils \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

WORKDIR /workspace

# Install KAS inside an isolated Python environment
RUN python3 -m venv /opt/kas-venv

RUN /opt/kas-venv/bin/pip install --no-cache-dir "kas==4.8"

ENV PATH="/opt/kas-venv/bin:${PATH}"
