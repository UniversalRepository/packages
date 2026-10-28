ci_config() {
    ARCH=${ARCH:-${UREPO_ALPINE_ARCH:-$(uname -m)}}
    PKGS_DIR=${PKGS_DIR:-$UREPO_ROOT/alpine}
    REPO_DIR=${REPO_DIR:-$UREPO_ROOT/builddir/alpine/packages}
    TEMPLATE=APKBUILD
    work=$UREPO_ROOT/builddir/alpine
    source "$UREPO_ROOT/alpine/build.sh"
}

ci_recipes() {
    local category dir
    for category in main community testing; do
        for dir in "$PKGS_DIR/$category"/*; do
            [[ -d $dir && ! -L $dir && -f $dir/APKBUILD ]] || continue
            printf '%s\n' "${dir##*/}"
        done
    done
}

ci_has_recipe() {
    alpine_recipe "$1" "$PKGS_DIR" >/dev/null
}

ci_prepare() {
    alpine_require
    [[ $ARCH == x86_64 && $(uname -m) == x86_64 ]] || die 'the Alpine selector currently supports native x86_64 only'
    [[ $PKGS_DIR == "$UREPO_ROOT/alpine" ]] || die 'Alpine PKGS_DIR must point to alpine in this checkout'
    [[ $REPO_DIR == "$work/packages" ]] || die 'Alpine REPO_DIR must point to builddir/alpine/packages in this checkout'
    alpine_prepare "$work"
    alpine_enter "$work" setup
}

ci_available() {
    alpine_enter "$work" available
}

ci_expected() {
    local recipe
    recipe=$(alpine_recipe "$1" "$PKGS_DIR")
    alpine_enter "$work" expected "$recipe" | awk -v category="${recipe%%/*}" '{ print category "/" $1, $2, $3 }'
}
