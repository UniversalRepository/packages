build() {
    case $1 in
        */*) set -- "${1%%/*}" "${1#*/}" ;;
        *) error 'expected target: DISTRO/PACKAGE'; exit 2 ;;
    esac
    for urepo_part do
        case $urepo_part in
            ''|[!a-zA-Z0-9]*|*[!a-zA-Z0-9._+-]*)
                error 'invalid target: use DISTRO/PACKAGE with simple names'
                exit 2
                ;;
        esac
    done

    [ -d "$UREPO_ROOT/$1" ] || die "unknown distribution: $1"
    [ -r "$UREPO_ROOT/$1/build.sh" ] || die "missing backend: $1/build.sh"
    [ -d "$UREPO_ROOT/$1/srcpkgs/$2" ] || die "unknown package: $1/$2"

    distro_build() { die 'backend does not define distro_build()'; }
    . "$UREPO_ROOT/$1/build.sh"
    distro_build "$2"
}
