distro_build() {
    local key=${UREPO_GPG_SIGN_KEY:-$UREPO_ROOT/keys/arch.key}
    local arch=${UREPO_ARCH_ARCH:-$(uname -m)}
    local work=$UREPO_ROOT/builddir/arch
    local pkg archive
    local GNUPGHOME=$work/gpg
    export GNUPGHOME
    local target
    local -a package_names=()

    for target in "$@"; do
        [[ $target == arch/* ]] || die "invalid arch target: $target"
        package_names+=("${target#*/}")
    done
    set -- "${package_names[@]}"

    for pkg in sudo unshare pacstrap pacman-key arch-chroot rsync gpg repo-add; do
        require "$pkg"
    done
    (( EUID != 0 )) || die 'run the Arch backend as a non-root user'
    [[ $arch == x86_64 && $(uname -m) == x86_64 ]] || die 'this Arch backend currently supports native x86_64 only'
    [[ -r $key ]] || die "cannot read signing key: $key"
    for pkg in "$@"; do
        [[ -f $UREPO_ROOT/arch/pkgs/$pkg/PKGBUILD ]] || die "missing PKGBUILD: $pkg"
    done

    mkdir -p "$work/$arch"
    mkdir -p -m 700 "$GNUPGHOME"
    gpg --batch --import "$key"

    cat > "$work/pacman.conf" <<'PACMAN'
[options]
Architecture = x86_64
SigLevel = Required DatabaseOptional
LocalFileSigLevel = Optional

[core]
Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch

[extra]
Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch
PACMAN

    info 'Preparing Arch build root'
    sudo -n unshare --mount --propagation private /bin/bash -euo pipefail -s -- \
        "$work" "$UREPO_ROOT/arch/pkgs" "$(id -u)" "$(id -g)" "$@" <<'BUILD'
work=$1
recipes=$2
builder_uid=$3
builder_gid=$4
shift 4
root=$work/root
unset SSL_CERT_FILE SSL_CERT_DIR GNUPGHOME

mkdir -p "$root"
mount --bind "$root" "$root"
trap 'umount -R "$root"' EXIT

pacman-key --init
pacman-key --populate archlinux
if [[ ! -f $root/.urepo-bootstrap ]]; then
    pacstrap -C "$work/pacman.conf" -M "$root" base base-devel archlinux-keyring meson sudo rsync
    touch "$root/.urepo-bootstrap"
fi
install -m 644 "$work/pacman.conf" "$root/etc/pacman.conf"
arch-chroot "$root" pacman -Syu --needed --noconfirm base base-devel archlinux-keyring meson sudo rsync

arch-chroot "$root" /bin/bash -euo pipefail -s -- "$builder_uid" "$builder_gid" <<'USER'
if ! getent group "$2" >/dev/null; then
    groupadd --gid "$2" builder
fi
if ! id builder >/dev/null 2>&1; then
    useradd --uid "$1" --gid "$2" --create-home --shell /bin/bash builder
fi
printf '%s\n' 'builder ALL=(root) NOPASSWD: /usr/bin/pacman' > /etc/sudoers.d/urepo-builder
chmod 0440 /etc/sudoers.d/urepo-builder
visudo --check --file /etc/sudoers.d/urepo-builder
USER

for pkg in "$@"; do
    printf '==> Building %s\n' "$pkg"
    mkdir -p "$root/build/$pkg"
    rsync -aL --delete --exclude=.git "$recipes/$pkg/" "$root/build/$pkg/"
    chown -R "$builder_uid:$builder_gid" "$root/build"
    arch-chroot "$root" runuser -u builder -- /bin/bash -euo pipefail -c '
        cd "/build/$1"
        export HOME=/home/builder
        export PKGDEST="$PWD/packages"
        mkdir -p "$PKGDEST"
        makepkg --syncdeps --cleanbuild --clean --noconfirm
    ' bash "$pkg"
    find "$root/build/$pkg/packages" -maxdepth 1 -type f -name '*.pkg.tar.*' -exec cp -t "$work/x86_64" -- {} +
done
chown -R "$builder_uid:$builder_gid" "$work/x86_64"
BUILD

    local -a archives=()
    mapfile -d '' -t archives < <(find "$work/$arch" -maxdepth 1 -type f -name '*.pkg.tar.*' ! -name '*.sig' -print0)
    (( ${#archives[@]} )) || die "no packages found in $work/$arch"
    info 'Signing Arch packages'
    for archive in "${archives[@]}"; do
        gpg --batch --yes --detach-sign --output "$archive.sig" "$archive"
    done
    repo-add --sign --verify --remove "$work/$arch/universalrepository.db.tar.gz" "${archives[@]}"
    info "Repository: $work/$arch"
}
