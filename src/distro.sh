build() {
    local target distro pkg part
    local -a distros=() packages=()
    local -A seen=()

    for target in "$@"; do
        [[ $target == */* ]] || { error 'expected target: DISTRO/PACKAGE'; exit 2; }
        distro=${target%%/*}
        pkg=${target#*/}
        for part in "$distro" "$pkg"; do
            case $part in
                ''|[!a-zA-Z0-9]*|*[!a-zA-Z0-9._+-]*)
                    error "invalid target: $target"
                    exit 2
                    ;;
            esac
        done
        [[ -d $UREPO_ROOT/$distro ]] || die "unknown distribution: $distro"
        [[ -r $UREPO_ROOT/$distro/build.sh ]] || die "missing backend: $distro/build.sh"
        [[ -d $UREPO_ROOT/$distro/srcpkgs/$pkg ]] || die "unknown package: $target"
        if [[ ! ${seen[$distro]+present} ]]; then
            distros+=("$distro")
            seen[$distro]=1
        fi
    done

    for distro in "${distros[@]}"; do
        (
            packages=()
            for target in "$@"; do
                [[ ${target%%/*} == "$distro" ]] || continue
                packages+=("${target#*/}")
            done
            distro_build() { die 'backend does not define distro_build()'; }
            source "$UREPO_ROOT/$distro/build.sh"
            distro_build "${packages[@]}"
        )
    done
}
