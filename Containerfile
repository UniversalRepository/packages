FROM registry.fedoraproject.org/fedora:44

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN <<'BASE_TOOLS'
dnf -y upgrade --refresh
packages=(
    bash ca-certificates coreutils curl findutils gawk grep sed
    git patch diffutils tar xz gzip bzip2 zstd unzip which
    util-linux shadow-utils sudo bubblewrap procps-ng
    openssh-clients rsync gnupg2 openssl
    python3 python3-black python3-flake8 ruff
    pacman arch-install-scripts
    rpm-build rpm-sign rpmdevtools createrepo_c
    dnf5-plugins mock mock-core-configs
    apk-tools debootstrap
)
dnf -y install --setopt=install_weak_deps=False "${packages[@]}"
dnf clean all
rm -rf /var/cache/dnf /var/cache/libdnf5
BASE_TOOLS

ARG XBPS_URL=https://repo-default.voidlinux.org/static/xbps-static-static-0.60.4_1.x86_64-musl.tar.xz
ARG XBPS_SHA256=603b3c55e9cabd5af79b461b929b14e1556a443c97b5714d188681c2172d9e28

RUN <<'STATIC_XBPS'
test "$(uname -m)" = x86_64
mkdir -p /opt/xbps
curl --fail --location --retry 3 --proto '=https' "$XBPS_URL" --output /tmp/xbps.tar.xz
printf '%s  /tmp/xbps.tar.xz\n' "$XBPS_SHA256" | sha256sum --check --strict -
tar --extract --xz --no-same-owner --file /tmp/xbps.tar.xz --directory /opt/xbps
chmod 0755 /opt/xbps
rm /tmp/xbps.tar.xz
STATIC_XBPS

ENV PATH="/opt/xbps/usr/bin:${PATH}"
ENV SSL_CERT_FILE=/etc/pki/tls/certs/ca-bundle.crt
ENV XBPS_ARCH=x86_64 XBPS_TARGET_ARCH=x86_64

ARG BUILDER_UID=1000
ARG BUILDER_GID=1000

RUN <<'BUILD_USER'
groupadd --gid "$BUILDER_GID" builder
groupadd --system xbuilder
useradd --uid "$BUILDER_UID" --gid builder --groups mock,xbuilder --create-home --shell /bin/bash builder
install -d -o builder -g builder /workspace
echo 'builder ALL=(root) NOPASSWD: ALL' > /etc/sudoers.d/builder
chmod 0440 /etc/sudoers.d/builder
visudo --check --file /etc/sudoers.d/builder
BUILD_USER

USER builder
WORKDIR /workspace

RUN <<'CHECK'
for tool in bash git bwrap python3 black ruff flake8 sudo rsync ssh xbps-install xbps-query xbps-rindex xbps-uunshare pacman pacstrap makepkg repo-add mock rpmbuild rpmsign createrepo_c apk debootstrap; do
    printf 'testing for %s... ' "$tool"
    command -v "$tool" > /dev/null || { printf 'not found\n'; exit 1; }
    printf 'OK\n'
done
xbps-install --version
xbps-rindex --version
python3 -c 'import sys; assert sys.version_info >= (3, 12)'
CHECK

CMD ["/bin/bash"]
