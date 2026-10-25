ci_config() {
    ARCH=${ARCH:-${UREPO_CHIMERA_ARCH:-$(uname -m)}}
    PKGS_DIR=${PKGS_DIR:-$UREPO_ROOT/chimera}
    REPO_DIR=${REPO_DIR:-$UREPO_ROOT/builddir/chimera/packages}
    TEMPLATE=template.py
    work=$UREPO_ROOT/builddir/chimera
    source "$UREPO_ROOT/chimera/build.sh"
    chimera_validate_overlay "$PKGS_DIR"
}

ci_recipes() {
    local category dir
    for category in main user; do
        for dir in "$PKGS_DIR/$category"/*; do
            [[ -d $dir && ! -L $dir && -f $dir/template.py ]] || continue
            printf '%s\n' "${dir##*/}"
        done
    done
}

ci_has_recipe() {
    chimera_recipe "$1" "$PKGS_DIR" >/dev/null
}

ci_prepare() {
    chimera_require
    [[ $ARCH == "$(uname -m)" ]] || die 'the Chimera selector currently supports native builds only'
    [[ $PKGS_DIR == "$UREPO_ROOT/chimera" ]] || die 'Chimera PKGS_DIR must point to the main/user overlay root in this checkout'
    chimera_prepare "$work"
    chimera_config "$scratch/config.ini" "$work" "$scratch/unused.rsa"
}

ci_available() {
    python3 "$UREPO_ROOT/chimera/metadata.py" available "$REPO_DIR" "$ARCH"
}

ci_expected() {
    local metadata recipe
    local -a args=()
    read -r -a args <<< "${UREPO_CHIMERA_CBUILD_ARGS:-}"
    recipe=$(chimera_recipe "$1" "$PKGS_DIR")
    metadata=$(cd -- "$work/cports" && ./cbuild -c "$scratch/config.ini" "${args[@]}" -a "$ARCH" dump "$recipe") || die "cannot read metadata: chimera/$1"
    python3 "$UREPO_ROOT/chimera/metadata.py" expected "$recipe" "$ARCH" <<< "$metadata"
}
