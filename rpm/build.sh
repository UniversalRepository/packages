distro_build() {
    local key=${UREPO_GPG_SIGN_KEY:-$UREPO_ROOT/keys/rpm.key}
    local sign_name=${UREPO_SIGN_NAME:-C57FBE5A22ED5000C8149B21A7CA149CF8A6B28C}
    local arch=${UREPO_RPM_ARCH:-$(uname -m)}
    local work=$UREPO_ROOT/builddir/rpm
    local pkg pkg_dir spec_file ID
    local -a elevate=() requirements=()
    local GNUPGHOME=$work/gpg
    export GNUPGHOME
    local target
    local -a package_names=()

    for target in "$@"; do
        [[ $target == rpm/* ]] || die "invalid rpm target: $target"
        package_names+=("${target#*/}")
    done
    set -- "${package_names[@]}"

    require rpm
    require rpmbuild
    require rpmsign
    require createrepo_c
    require gpg
    [[ -r /etc/os-release ]] || die 'cannot read /etc/os-release'
    source /etc/os-release
    case $ID in
        fedora) require dnf; require spectool ;;
        opensuse*|sles|sled) require zypper; require rpmdev-spectool; require rpmspec ;;
        *) die "unsupported RPM distribution: $ID" ;;
    esac
    if (( EUID != 0 )); then
        require sudo
        elevate=(sudo)
    fi
    [[ -r $key ]] || die "cannot read signing key: $key"
    [[ $key == /* ]] || key=$PWD/$key
    work=$work/$ID
    GNUPGHOME=$work/gpg
    mkdir -p "$work"/{SOURCES,SPECS,BUILD,BUILDROOT,SRPMS,RPMS}
    mkdir -p -m 700 "$GNUPGHOME"
    gpg --batch --import "$key"

    for pkg in "$@"; do
        pkg_dir=$UREPO_ROOT/rpm/srcpkgs/$pkg
        spec_file=$pkg_dir/$pkg.spec
        [[ -f $spec_file ]] || die "missing spec: $spec_file"
        info "Preparing $pkg"
        (
            cd "$pkg_dir"
            case $ID in
                fedora)
                    spectool -g -C "$work/SOURCES" "$spec_file"
                    "${elevate[@]}" dnf builddep -y "$spec_file"
                    ;;
                *)
                    rpmdev-spectool -g -C "$work/SOURCES" "$spec_file"
                    rpmspec -q --buildrequires "$spec_file" > "$work/buildrequires"
                    mapfile -t requirements < "$work/buildrequires"
                    if (( ${#requirements[@]} )); then
                        "${elevate[@]}" zypper --non-interactive install "${requirements[@]}"
                    fi
                    ;;
            esac
            info "Building $pkg"
            rpmbuild --define "_topdir $work" --define "_specdir $pkg_dir" \
                --target "$arch" -ba "$spec_file"
        )
    done
    rpm_create_repo "$work/RPMS"
    info "Repository: $work/RPMS"
}

rpm_create_repo() {
    local repo=$1 rpm_file
    local -a packages=()
    shopt -s nullglob
    packages=("$repo"/*/*.rpm)
    (( ${#packages[@]} )) || die "no RPM packages found in $repo"
    for rpm_file in "${packages[@]}"; do
        info "Signing $rpm_file"
        rpmsign --define "_gpg_name $sign_name" --define "_gpg_path $GNUPGHOME" \
            --addsign "$rpm_file"
    done
    createrepo_c "$repo"
    gpg --batch --yes --local-user "$sign_name" --detach-sign --armor "$repo/repodata/repomd.xml"
    gpg --armor --export "$sign_name" > "$repo/repodata/repomd.xml.key"
}
