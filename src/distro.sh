build() {
    distros=
    for target do
        case $target in
            */*) distro=${target%%/*}; pkg=${target#*/} ;;
            *) error 'expected target: DISTRO/PACKAGE'; exit 2 ;;
        esac
        for part in "$distro" "$pkg"; do
            case $part in
                ''|[!a-zA-Z0-9]*|*[!a-zA-Z0-9._+-]*)
                    error "invalid target: $target"
                    exit 2
                    ;;
            esac
        done

        [ -d "$UREPO_ROOT/$distro" ] || die "unknown distribution: $distro"
        [ -r "$UREPO_ROOT/$distro/build.sh" ] || die "missing backend: $distro/build.sh"
        [ -d "$UREPO_ROOT/$distro/srcpkgs/$pkg" ] || die "unknown package: $target"
        case " $distros " in
            *" $distro "*) ;;
            *) distros="$distros $distro" ;;
        esac
    done

    for distro in $distros; do
        (
            packages=
            for target do
                [ "${target%%/*}" = "$distro" ] || continue
                packages="$packages ${target#*/}"
            done
            set -- $packages
            distro_build() { die 'backend does not define distro_build()'; }
            . "$UREPO_ROOT/$distro/build.sh"
            distro_build "$@"
        )
    done
}
