#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

UREPO_ROOT=${UREPO_ROOT:-$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)}
source "$UREPO_ROOT/src/cli.sh"

usage() {
    cat <<'HELP'
usage: .ci/unbuilt.sh DISTRO [PACKAGE]

env:
  ARCH       Target architecture (default: backend setting or uname -m)
  PKGS_DIR   Recipe directory (default: supplied by the distro adapter)
  REPO_DIR   Downloaded repository (default: supplied by the distro adapter)
HELP
}

case ${1:-} in
    -h|--help) usage; exit 0 ;;
    '') usage >&2; exit 2 ;;
esac
DISTRO=$1
shift
case $DISTRO in
    [!a-zA-Z0-9]*|*[!a-zA-Z0-9._+-]*) die "invalid distribution: $DISTRO" ;;
esac

adapter=$UREPO_ROOT/.ci/backends/$DISTRO.sh
[[ -r $adapter ]] || die "missing selection adapter: .ci/backends/$DISTRO.sh"
source "$adapter" >&2
for hook in ci_config ci_prepare ci_expected ci_available; do
    declare -F "$hook" >/dev/null || die "missing $hook in $adapter"
done
ci_config >&2
: "${ARCH:?adapter must set ARCH}" "${PKGS_DIR:?adapter must set PKGS_DIR}" "${REPO_DIR:?adapter must set REPO_DIR}" "${TEMPLATE:?adapter must set TEMPLATE}"

has_recipe() {
    local file IFS=
    for file in "$PKGS_DIR/$1"/$TEMPLATE; do
        [[ -f $file ]] && return 0
    done
    return 1
}
if (( $# == 0 )); then
    for dir in "$PKGS_DIR"/*; do
        [[ -d $dir && ! -L $dir ]] || continue
        if has_recipe "${dir##*/}"; then
            set -- "$@" "${dir##*/}"
        fi
    done
fi
(( $# )) || exit 0
for recipe in "$@"; do
    case $recipe in
        ''|[!a-zA-Z0-9]*|*[!a-zA-Z0-9._+-]*) die "invalid package: $recipe" ;;
    esac
    has_recipe "$recipe" || die "missing recipe: $DISTRO/$recipe"
done

scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

normalize() {
    awk 'NF != 3 { bad = 1 } { print $1, $2, $3 } END { exit bad }' "$1" > "$scratch/checked" || die "invalid metadata records: $2"
    sort -u "$scratch/checked" > "$1"
}

ci_prepare >&2
ci_available > "$scratch/available"
normalize "$scratch/available" "$DISTRO repository"
: > "$scratch/queue"
declare -A seen=()
for recipe in "$@"; do
    [[ ! ${seen[$recipe]+present} ]] || continue
    seen[$recipe]=1
    ci_expected "$recipe" > "$scratch/expected"
    normalize "$scratch/expected" "$DISTRO/$recipe"
    if [[ ! -s $scratch/expected ]]; then
        info "Skipping $DISTRO/$recipe: unsupported architecture $ARCH"
        continue
    fi
    comm -23 "$scratch/expected" "$scratch/available" > "$scratch/missing"
    if [[ -s $scratch/missing ]]; then
        info "Queued $DISTRO/$recipe ($ARCH)"
        printf '%s/%s\n' "$DISTRO" "$recipe" >> "$scratch/queue"
    else
        info "Skipping $DISTRO/$recipe: already built ($ARCH)"
    fi
done
cat "$scratch/queue"
