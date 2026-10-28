distro_build() {
    local work=$UREPO_ROOT/builddir/alpine
    local arch=${UREPO_ALPINE_ARCH:-${ARCH:-$(uname -m)}}
    local key=${UREPO_ALPINE_SIGN_KEY:-${SIGN_KEY:-$UREPO_ROOT/keys/alpine.pem}}
    local target recipe metadata name version
    local -a recipes=() ordered=()
    local -A owners=() states=()

    alpine_require
    [[ $arch == x86_64 && $(uname -m) == x86_64 ]] || die 'the Alpine backend currently supports native x86_64 only'
    [[ -r $key ]] || die "cannot read signing key: $key"
    key=$(realpath -- "$key")
    openssl rsa -in "$key" -passin pass: -check -noout >/dev/null || die 'Alpine requires an unencrypted RSA private key'
    for target in "$@"; do
        [[ $target == alpine/* ]] || die "invalid Alpine target: $target"
        recipe=$(alpine_recipe "${target#*/}" "$UREPO_ROOT/alpine")
        recipes+=("$recipe")
    done

    alpine_prepare "$work"
    openssl rsa -in "$key" -passin pass: -pubout -out "$work/config/universalrepository.rsa.pub"
    cp -- "$work/config/universalrepository.rsa.pub" "$work/packages/universalrepository.rsa.pub"
    alpine_enter "$work" setup
    alpine_order "$work" "${recipes[@]}"
    for recipe in "${ordered[@]}"; do
        metadata=$(alpine_enter "$work" expected "$recipe")
        [[ -n $metadata ]] || die "alpine/$recipe: unsupported architecture $arch"
        while read -r name version _; do
            rm -f -- "$work/packages/${recipe%%/*}/$arch/$name-$version.apk"
        done <<< "$metadata"
        info "Building Alpine edge package: $recipe"
        alpine_enter "$work" build "$recipe" "$key"
        alpine_enter "$work" check-built "$recipe"
    done
    info 'Indexing and verifying Alpine repositories'
    alpine_enter "$work" index "" "$key"
    info "Repository: $work/packages"
}

alpine_require() {
    local tool
    (( EUID != 0 )) || die 'run the Alpine backend as a non-root user'
    for tool in git sudo bwrap apk openssl realpath; do
        require "$tool"
    done
}

alpine_recipe() {
    local name=$1 overlay=$2 category found=
    case $name in
        ''|[!a-zA-Z0-9]*|*[!a-zA-Z0-9._+-]*) die "invalid Alpine package: $name (expected alpine/PACKAGE)" ;;
    esac
    for category in main community testing; do
        [[ -f $overlay/$category/$name/APKBUILD ]] || continue
        [[ -z $found ]] || die "duplicate Alpine package: $name"
        found=$category/$name
    done
    [[ -n $found ]] || die "missing Alpine recipe: $name"
    printf '%s\n' "$found"
}

alpine_prepare() {
    local work=$1 tree=$1/aports category item name
    local ref=${UREPO_ALPINE_APORTS_REF:-master}
    local -A seen=()
    for category in main community testing; do
        for item in "$UREPO_ROOT/alpine/$category"/*; do
            [[ -d $item || -L $item ]] || continue
            [[ ! -L $item && -f $item/APKBUILD && ! -L $item/APKBUILD ]] || die "invalid Alpine recipe directory: $item"
            name=${item##*/}
            [[ ! ${seen[$name]+present} ]] || die "duplicate Alpine package: $name"
            seen[$name]=1
        done
    done
    mkdir -p "$work/config" "$work/packages" "$work/sources"
    info 'Preparing Alpine edge sources'
    if [[ ! -d $tree/.git ]]; then
        git clone --depth 1 https://gitlab.alpinelinux.org/alpine/aports.git "$tree"
    fi
    git -C "$tree" fetch --depth 1 origin "$ref"
    git -C "$tree" reset --hard FETCH_HEAD
    git -C "$tree" clean -fdx
    for category in main community testing; do
        mkdir -p "$tree/$category"
        for item in "$UREPO_ROOT/alpine/$category"/*; do
            [[ -d $item ]] || continue
            name=${item##*/}
            rm -rf -- "$tree/main/$name" "$tree/community/$name" "$tree/testing/$name"
            cp -RP -- "$item" "$tree/$category/$name"
        done
        printf '%s\n' \
            'https://dl-cdn.alpinelinux.org/alpine/edge/main' \
            'https://dl-cdn.alpinelinux.org/alpine/edge/community' \
            'https://dl-cdn.alpinelinux.org/alpine/edge/testing' > "$tree/$category/.rootbld-repositories"
    done
    cp -- "$UREPO_ROOT/alpine/abuild.conf" "$work/config/abuild.conf"
}

alpine_enter() {
    local work=$1
    shift
    sudo -n bash "$UREPO_ROOT/alpine/root.sh" "$work" "$UREPO_ROOT/alpine" "$(id -u)" "$(id -g)" "$@"
}

alpine_order() {
    local work=$1 category item recipe metadata name version
    shift
    for category in main community testing; do
        for item in "$UREPO_ROOT/alpine/$category"/*; do
            [[ -f $item/APKBUILD ]] || continue
            recipe=$category/${item##*/}
            metadata=$(alpine_enter "$work" expected "$recipe")
            while read -r name version _; do
                [[ -n $name ]] || continue
                [[ ! ${owners[$name]+present} || ${owners[$name]} == "$recipe" ]] || die "duplicate Alpine output: $name"
                owners[$name]=$recipe
            done <<< "$metadata"
        done
    done
    for recipe in "$@"; do
        alpine_visit "$work" "$recipe"
    done
}

alpine_visit() {
    local work=$1 recipe=$2 dependency dependencies
    case ${states[$recipe]:-} in
        done) return ;;
        visiting) die "Alpine dependency cycle: $recipe" ;;
    esac
    states[$recipe]=visiting
    dependencies=$(alpine_enter "$work" dependencies "$recipe")
    while read -r dependency; do
        [[ -n $dependency && $dependency != '!'* ]] || continue
        dependency=${dependency%%[=\<\>\~]*}
        [[ ${owners[$dependency]+present} && ${owners[$dependency]} != "$recipe" ]] || continue
        alpine_visit "$work" "${owners[$dependency]}"
    done <<< "$dependencies"
    states[$recipe]='done'
    ordered+=("$recipe")
}
