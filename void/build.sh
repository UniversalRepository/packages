distro_build() {
    set -eu

    require git
    require xbps-rindex
    key=${UREPO_VOID_SIGN_KEY:-$UREPO_ROOT/keys/void.pem}
    [ -r "$key" ] || die "cannot read signing key: $key"
    [ -n "${UREPO_VOID_SIGNED_BY:-}" ] || die 'UREPO_VOID_SIGNED_BY is required'
    case $key in
        /*) ;;
        *) key=$PWD/$key ;;
    esac

    recipes=$UREPO_ROOT/void
    work=$UREPO_ROOT/builddir/void
    tree=$work/void-packages
    TMPDIR=$work/tmp
    export TMPDIR
    mkdir -p "$TMPDIR" "$work/hostdir"

    info 'Preparing Void sources'
    void_checkout "$tree"
    void_overlay "$recipes/srcpkgs" "$tree/srcpkgs"
    void_overlay "$recipes/common" "$tree/common" shlibs
    if [ -f "$recipes/common/shlibs" ]; then
        void_shlibs "$recipes/common/shlibs" "$tree/common/shlibs" > "$TMPDIR/shlibs"
        mv "$TMPDIR/shlibs" "$tree/common/shlibs"
    fi
    if [ -d "$recipes/etc" ]; then
        cp -RP "$recipes/etc/." "$tree/etc/"
    fi

    for pkg do
        info "Building $pkg"
        (
            cd "$tree"
            set -f
            set -- ${UREPO_VOID_XBPS_ARGS:-} -m "$work/masterdir" -H "$work/hostdir" pkg "$pkg"
            ./xbps-src "$@"
        )
        info "Successfully built $pkg"
    done

    info 'Indexing and signing packages'
    void_sign "$work/hostdir/binpkgs"
    info "Repository: $work/hostdir/binpkgs"
}

void_checkout() {
    if [ ! -d "$1/.git" ]; then
        git clone --depth 1 https://github.com/void-linux/void-packages.git "$1"
        return
    fi
    (
        cd "$1"
        git reset --hard
        git clean -fdx
        git pull --ff-only
    )
}

void_overlay() {
    for item in "$1"/* "$1"/.[!.]* "$1"/..?*; do
        [ -e "$item" ] || [ -L "$item" ] || continue
        name=${item##*/}
        [ "$name" != "${3:-}" ] || continue
        rm -rf "$2/$name"
        cp -RP "$item" "$2/$name"
    done
}

void_shlibs() {
    awk '
        FILENAME == ARGV[1] {
            if (NF && $1 !~ /^#/) {
                name = $1
                sub(/\.so.*/, "", name)
                replace[name] = 1
                lines[++count] = $0
            }
            next
        }
        {
            name = $1
            sub(/\.so.*/, "", name)
            if (!(name in replace)) print
        }
        END { for (i = 1; i <= count; i++) print lines[i] }
    ' "$1" "$2"
}

void_sign() {
    repo=$1
    set -- "$repo"/*.xbps
    if [ -f "$1" ]; then
        for index in "$repo"/*-repodata; do
            [ -f "$index" ] || continue
            arch=${index##*/}
            XBPS_TARGET_ARCH=${arch%-repodata} xbps-rindex -cC "$repo"
        done
        xbps-rindex --force -a "$@"
        for pkg in "$@"; do
            if [ -e "$pkg.sig2" ]; then
                xbps-rindex --force --privkey "$key" --sign-pkg "$pkg"
            else
                xbps-rindex --privkey "$key" --sign-pkg "$pkg"
            fi
        done
        for index in "$repo"/*-repodata; do
            [ -f "$index" ] || continue
            arch=${index##*/}
            XBPS_TARGET_ARCH=${arch%-repodata} xbps-rindex \
                --privkey "$key" --signedby "$UREPO_VOID_SIGNED_BY" --sign "$repo"
        done
    fi
    for dir in "$repo"/*; do
        [ -d "$dir" ] || continue
        (void_sign "$dir")
    done
}
