ci_config() {
    ARCH=${ARCH:-${UREPO_ARCH_ARCH:-$(uname -m)}}
    PKGS_DIR=${PKGS_DIR:-$UREPO_ROOT/arch/pkgs}
    REPO_DIR=${REPO_DIR:-$UREPO_ROOT/builddir/arch/$ARCH}
    TEMPLATE=PKGBUILD
}

ci_prepare() {
    require makepkg
    require pacman
}

ci_available() {
    local archive identity arch
    for archive in "$REPO_DIR"/*.pkg.tar.*; do
        [[ -f $archive && $archive != *.sig ]] || continue
        identity=$(pacman -Qp -- "$archive") || die "cannot read package: $archive"
        arch=${archive##*-}
        arch=${arch%%.pkg.tar.*}
        printf '%s %s\n' "$identity" "$arch"
    done
}

ci_expected() {
    local metadata
    metadata=$(cd -- "$PKGS_DIR/$1" && CARCH="$ARCH" makepkg --printsrcinfo) || die "cannot read metadata: arch/$1"
    awk -v target_arch="$ARCH" '
        function emit(    archs, n, a, i) {
            if (!name) return
            archs = package_archs ? package_archs : base_archs
            n = split(archs, a, " ")
            for (i = 1; i <= n; i++) {
                if (a[i] == target_arch || a[i] == "any") {
                    print name, (epoch && epoch != "0" ? epoch ":" : "") version "-" release, a[i]
                    return
                }
            }
        }
        $1 == "pkgver" { version = $3 }
        $1 == "pkgrel" { release = $3 }
        $1 == "epoch" { epoch = $3 }
        $1 == "pkgname" { emit(); name = $3; package_archs = "" }
        $1 == "arch" {
            if (name) package_archs = package_archs " " $3
            else base_archs = base_archs " " $3
        }
        END {
            if (!name || !version || !release || !base_archs) exit 1
            emit()
        }
    ' <<< "$metadata" || die "incomplete metadata: arch/$1"
}
