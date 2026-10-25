distro_build() {
    local work=$UREPO_ROOT/builddir/chimera
    local arch=${UREPO_CHIMERA_ARCH:-${ARCH:-$(uname -m)}}
    local key=${UREPO_CHIMERA_SIGN_KEY:-${SIGN_KEY:-$UREPO_ROOT/keys/chimera.rsa}}
    local target recipe category metadata
    local -a packages=()

    chimera_validate_overlay "$UREPO_ROOT/chimera"
    chimera_require
    [[ $arch == "$(uname -m)" ]] || die 'the Chimera backend currently supports native builds only'
    [[ -r $key ]] || die "cannot read signing key: $key"
    key=$(realpath -- "$key")
    for target in "$@"; do
        [[ $target == chimera/* ]] || die "invalid Chimera target: $target"
        recipe=$(chimera_recipe "${target#*/}" "$UREPO_ROOT/chimera")
        packages+=("$recipe")
    done

    chimera_prepare "$work"
    [[ -f $work/cports/etc/build_profiles/$arch.ini ]] || die "unsupported Chimera architecture: $arch"
    mkdir -p "$work/keys" "$work/packages"
    openssl rsa -in "$key" -passin pass: -check -noout >/dev/null || die 'Chimera requires an unencrypted RSA private key'
    openssl rsa -in "$key" -passin pass: -pubout -out "$work/keys/universalrepository.rsa.pub"
    cp -- "$work/keys/universalrepository.rsa.pub" "$work/packages/universalrepository.rsa.pub"
    chimera_config "$work/config.ini" "$work" "$key"

    chimera_cbuild "$work" bootstrap-update
    chimera_cbuild "$work" relink-subpkgs
    chimera_validate_overlay "$work/cports"
    info "Building Chimera packages: ${packages[*]}"
    chimera_cbuild "$work" -f bulk-pkg "${packages[@]}"
    chimera_cbuild "$work" unstage
    for recipe in "${packages[@]}"; do
        metadata=$(chimera_cbuild "$work" dump "$recipe")
        python3 "$UREPO_ROOT/chimera/metadata.py" check-built "$recipe" "$arch" "$work/packages" <<< "$metadata"
    done

    info 'Indexing and verifying Chimera repositories'
    for category in main user; do
        for recipe in "$work/packages/$category" "$work/packages/$category/debug"; do
            [[ -d $recipe/$arch ]] || continue
            chimera_cbuild "$work" index "$recipe"
            chimera_verify "$recipe/$arch" "$work/keys"
        done
    done
    info "Repository: $work/packages"
}

chimera_require() {
    local tool
    (( EUID != 0 )) || die 'run the Chimera backend as a non-root user'
    for tool in git python3 bwrap openssl realpath; do
        require "$tool"
    done
    require "${CBUILD_APK_PATH:-apk}"
    python3 -c 'import sys; sys.exit(sys.version_info < (3, 12))' || die 'Chimera requires Python 3.12 or newer'
    [[ $("${CBUILD_APK_PATH:-apk}" --version) == 'apk-tools 3.'* ]] || die 'Chimera requires apk-tools 3.x'
}

chimera_recipe() {
    local recipe=$1 recipes=$2 category found=
    case $recipe in
        ''|[!a-zA-Z0-9]*|*[!a-zA-Z0-9._+-]*) die "invalid Chimera package: $recipe (expected chimera/PACKAGE)" ;;
    esac
    for category in main user; do
        [[ -f $recipes/$category/$recipe/template.py ]] || continue
        [[ -z $found ]] || die "duplicate Chimera package: $recipe (main and user)"
        found=$category/$recipe
    done
    [[ -n $found ]] || die "missing Chimera recipe: $recipe"
    printf '%s\n' "$found"
}

chimera_validate_overlay() {
    local recipes=$1 category item name
    local -A seen=()
    for category in main user; do
        for item in "$recipes/$category"/*; do
            [[ -d $item || -L $item ]] || continue
            name=${item##*/}
            [[ ! ${seen[$name]+present} ]] || die "duplicate Chimera package: $name (main and user)"
            seen[$name]=$category
        done
    done
}

chimera_prepare() {
    local work=$1 tree=$1/cports category item name
    local ref=${UREPO_CHIMERA_CPORTS_REF:-master}
    chimera_validate_overlay "$UREPO_ROOT/chimera"
    mkdir -p "$work"
    info 'Preparing Chimera sources'
    if [[ ! -d $tree/.git ]]; then
        git clone --depth 1 https://github.com/chimera-linux/cports.git "$tree"
    fi
    git -C "$tree" fetch --depth 1 origin "$ref"
    git -C "$tree" reset --hard FETCH_HEAD
    git -C "$tree" clean -fdx
    for category in main user; do
        for item in "$UREPO_ROOT/chimera/$category"/*; do
            [[ -d $item || -L $item ]] || continue
            name=${item##*/}
             rm -rf -- "$tree/main/$name" "$tree/user/$name"
            cp -RP -- "$item" "$tree/$category/$name"
        done
    done
}

chimera_config() {
    python3 - "$1" "$2" "$3" <<'PY'
import configparser
from pathlib import Path
import sys

config_path, work, key = map(Path, sys.argv[1:])
config = configparser.ConfigParser(interpolation=None)
config["build"] = {
    "build_root": str(work / "bldroot"),
    "repository": str(work / "packages"),
    "stage_repository": str(work / "pkgstage"),
    "sources": str(work / "sources"),
    "cbuild_cache_path": str(work / "cbuild_cache"),
    "maintainer": "UniversalRepository",
}
config["signing"] = {"key": str(key), "keys": str(work / "keys")}
for section in config.values():
    for name, value in list(section.items()):
        section[name] = value.replace("%", "%%")
with config_path.open("w") as stream:
    config.write(stream)
PY
}

chimera_cbuild() {
    local work=$1
    shift
    local -a args=()
    read -r -a args <<< "${UREPO_CHIMERA_CBUILD_ARGS:-}"
    (cd -- "$work/cports" && ./cbuild -c "$work/config.ini" "${args[@]}" -a "${UREPO_CHIMERA_ARCH:-${ARCH:-$(uname -m)}}" "$@")
}

chimera_verify() {
    python3 "$UREPO_ROOT/chimera/metadata.py" verify "$1" "$2"
}
