ci_config() {
    ARCH=${ARCH:-${XBPS_TARGET_ARCH:-$(uname -m)}}
    PKGS_DIR=${PKGS_DIR:-$UREPO_ROOT/void/srcpkgs}
    REPO_DIR=${REPO_DIR:-$UREPO_ROOT/builddir/void/hostdir/binpkgs}
    TEMPLATE=template
    tree=$UREPO_ROOT/builddir/void/void-packages
}

ci_prepare() {
    require git
    require xbps-uhelper
    source "$UREPO_ROOT/void/build.sh"
    void_prepare "$UREPO_ROOT/void" "$UREPO_ROOT/builddir/void" "$tree" "$scratch/tmp"
    if [[ $PKGS_DIR != "$UREPO_ROOT/void/srcpkgs" ]]; then
        void_overlay "$PKGS_DIR" "$tree/srcpkgs"
    fi
}

ci_available() {
    local archive filename pkgver arch
    [[ -d $REPO_DIR ]] || return 0
    find "$REPO_DIR" -type f -name '*.xbps' -print0 > "$scratch/xbps"
    while IFS= read -r -d '' archive; do
        filename=${archive##*/}
        filename=${filename%.xbps}
        arch=${filename##*.}
        pkgver=${filename%.*}
        printf '%s %s %s\n' "${pkgver%-*}" "${pkgver##*-}" "$arch"
    done < "$scratch/xbps"
}

void_metadata() {
    local metadata key value pattern matched=0 allowed=1
    local pkgname= version= revision= archs= subpackages=
    local -a patterns=()
    local -a xbps_args=()
    read -r -a xbps_args <<< "${UREPO_VOID_XBPS_ARGS:-}"
    metadata=$(cd -- "$tree" && XBPS_ARCH="$ARCH" XBPS_TARGET_ARCH="$ARCH" \
        ./xbps-src "${xbps_args[@]}" -A "$ARCH" -m "$scratch/masterdir" -H "$UREPO_ROOT/builddir/void/hostdir" show-pkg-var-dump "$1") || die "cannot read metadata: void/$1"
    while IFS=: read -r key value; do
        value=${value# }
        case $key in
            pkgname) pkgname=$value ;;
            version) version=$value ;;
            revision) revision=$value ;;
            archs) archs=$value ;;
            subpackages) subpackages=$value ;;
        esac
    done <<< "$metadata"
    [[ -n $pkgname && -n $version && -n $revision ]] || die "incomplete metadata: void/$1"
    if [[ -n $archs ]]; then
        allowed=0
        read -r -a patterns <<< "$archs"
        for pattern in "${patterns[@]}"; do
            if [[ $ARCH == ${pattern#\~} ]]; then
                matched=1
                [[ $pattern == '~'* ]] || allowed=1
                break
            fi
        done
        if (( ! matched )) && [[ $pattern == '~'* ]]; then
            allowed=1
        fi
    fi
    if (( allowed )); then
        printf '%s %s_%s %s\n' "$1" "$version" "$revision" "$ARCH"
    fi
    void_subpackages=$subpackages
    void_supported=$allowed
}

ci_expected() {
    local recipe=$1 sub void_subpackages void_supported
    local -a subpackages=()
    void_metadata "$recipe"
    (( void_supported )) || return 0
    read -r -a subpackages <<< "$void_subpackages"
    for sub in "${subpackages[@]}"; do
        if [[ ! -e $tree/srcpkgs/$sub && ! -L $tree/srcpkgs/$sub ]]; then
            ln -s -- "$recipe" "$tree/srcpkgs/$sub"
        fi
        void_metadata "$sub"
    done
}
