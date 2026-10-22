ci_config() {
    local ID
    source /etc/os-release
    ARCH=${ARCH:-${UREPO_RPM_ARCH:-$(uname -m)}}
    PKGS_DIR=${PKGS_DIR:-$UREPO_ROOT/rpm/srcpkgs}
    rpm_work=$UREPO_ROOT/builddir/rpm/$ID
    REPO_DIR=${REPO_DIR:-$rpm_work/RPMS}
    TEMPLATE='*.spec'
}

ci_prepare() {
    require rpm
    require rpmspec
}

ci_available() {
    local archive
    [[ -d $REPO_DIR ]] || return 0
    find "$REPO_DIR" -type f -name '*.rpm' ! -name '*.src.rpm' ! -name '*.nosrc.rpm' -print0 > "$scratch/rpms"
    while IFS= read -r -d '' archive; do
        rpm -qp --queryformat '%{NAME} %{EPOCHNUM}:%{VERSION}-%{RELEASE} %{ARCH}\n' "$archive"
    done < "$scratch/rpms"
}

ci_expected() {
    local spec=$PKGS_DIR/$1/$1.spec records
    [[ -f $spec ]] || die "missing spec: $spec"
    records=$(cd -- "$PKGS_DIR/$1" && rpmspec -q --rpms --target "$ARCH" \
        --define "_topdir $rpm_work" --define "_specdir $PKGS_DIR/$1" \
        --queryformat '%{NAME} %{EPOCHNUM}:%{VERSION}-%{RELEASE} %{ARCH}\n' "$1.spec") || die "cannot read metadata: rpm/$1"
    [[ -n $records ]] || die "empty metadata: rpm/$1"
    awk -v arch="$ARCH" '$3 == arch || $3 == "noarch"' <<< "$records"
}
