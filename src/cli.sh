info() { message '1;34' '==>' "$*"; }
warn() { message '1;33' 'warning:' "$*"; }
error() { message '1;31' 'error:' "$*"; }
die() { error "$*"; exit 1; }
require() { command -v "$1" >/dev/null 2>&1 || die "command not found: $1"; }

message() {
    if [ -t 2 ] && [ -z "${NO_COLOR+x}" ] && [ "${TERM:-dumb}" != dumb ]; then
        printf '\033[%sm%s\033[0m %s\n' "$1" "$2" "$3" >&2
    else
        printf '%s %s\n' "$2" "$3" >&2
    fi
}

usage() {
    info "UniversalRepository Packages"
    printf '%s\n' \
        'Usage: urepo build DISTRO/PACKAGE [DISTRO/PACKAGE ...]' \
        '       urepo help' \
        '' \
        'Build native packages sequentially using their distribution backends.' \
        'Example: urepo build void/foo void/bar' \
        '' \
        'Set NO_COLOR to disable terminal colors.'
}

main() {
    case ${1:-} in
        '')
            [ "$#" -eq 0 ] || { error 'empty command'; exit 2; }
            usage
            ;;
        help|-h|--help)
            [ "$#" -eq 1 ] || { error 'help takes no arguments'; exit 2; }
            usage
            ;;
        build)
            [ "$#" -ge 2 ] || {
                error 'expected: urepo build DISTRO/PACKAGE [DISTRO/PACKAGE ...]'
                exit 2
            }
            shift
            build "$@"
            ;;
        *)
            error "unknown command $1, see 'urepo help'"
            exit 2
            ;;
    esac
}
