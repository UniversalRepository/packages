#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export ABUILD_USERDIR=/home/builder/.abuild
export APORTSDIR=/build/aports REPODEST=/build/packages SRCDEST=/build/sources
arch=$(apk --print-arch)
action=$1
recipe=${2:-}

case $action in
    expected)
        exec abuild -C "$APORTSDIR/$recipe" urepo_metadata
        ;;
    dependencies)
        exec abuild -C "$APORTSDIR/$recipe" urepo_dependencies
        ;;
    build)
        exec abuild -C "$APORTSDIR/$recipe" -f rootbld
        ;;
    check-built)
        abuild -C "$APORTSDIR/$recipe" urepo_metadata |
            python3 /build/backend/metadata.py check-built "$REPODEST/${recipe%%/*}/$arch"
        ;;
    available)
        exec python3 /build/backend/metadata.py available "$REPODEST" "$arch"
        ;;
    index)
        for category in main community testing; do
            repo=$REPODEST/$category/$arch
            [[ -d $repo ]] || continue
            shopt -s nullglob
            packages=("$repo"/*.apk)
            (( ${#packages[@]} )) || continue
            trap 'rm -f -- "$repo/APKINDEX.tar.gz.pending"' EXIT
            apk index --rewrite-arch "$arch" --output "$repo/APKINDEX.tar.gz.pending" "${packages[@]}"
            abuild-sign "$repo/APKINDEX.tar.gz.pending"
            python3 /build/backend/metadata.py verify "$repo" "$ABUILD_USERDIR" "$arch" "$repo/APKINDEX.tar.gz.pending"
            mv -- "$repo/APKINDEX.tar.gz.pending" "$repo/APKINDEX.tar.gz"
            trap - EXIT
        done
        ;;
    *) printf 'error: unknown Alpine action: %s\n' "$action" >&2; exit 1 ;;
esac
