validate_targets() {
    local target distro pkg part
    for target in "$@"; do
        [[ $target == */* ]] || {
            error 'expected target: DISTRO/PACKAGE'
            exit 2
        }

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
    done
}

build() {
    local target distro
    local -a distros=() targets=()
    local -A seen=()

    validate_targets "$@"
    for target in "$@"; do
        distro=${target%%/*}

        if [[ ! ${seen[$distro]+present} ]]; then
            distros+=("$distro")
            seen[$distro]=1
        fi
    done

    for distro in "${distros[@]}"; do
        (
            targets=()
            for target in "$@"; do
                [[ ${target%%/*} == "$distro" ]] || continue
                targets+=("$target")
            done

            distro_build() {
                die 'backend does not define distro_build()'
            }

            source "$UREPO_ROOT/$distro/build.sh"
            distro_build "${targets[@]}"
        )
    done
}
