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
        'Usage: urepo build [-c] DISTRO/PACKAGE [DISTRO/PACKAGE ...]' \
        '       urepo pkg [-c] DISTRO/PACKAGE [DISTRO/PACKAGE ...]' \
        '       urepo help' \
        '' \
        'Build native packages sequentially using their distribution backends.' \
        'Example: urepo build void/foo void/bar' \
        'Use -c/--container to build with local Podman or Docker.' \
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
        build|pkg)
            shift
            local container=0
            while (( $# )); do
                case $1 in
                    -c|--container) container=1; shift ;;
                    --) shift; break ;;
                    -*) error "unknown build option: $1"; exit 2 ;;
                    *) break ;;
                esac
            done
            [ "$#" -ge 1 ] || {
                error 'expected: urepo build [-c] DISTRO/PACKAGE [DISTRO/PACKAGE ...]'
                exit 2
            }
            if (( container )); then
                source "$UREPO_ROOT/src/container.sh"
                container_build "$@"
            else
                build "$@"
            fi
            ;;
        *)
            error "unknown command $1, see 'urepo help'"
            exit 2
            ;;
    esac
}
