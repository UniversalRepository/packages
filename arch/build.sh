distro_build() {
    set -eu

    check_depenth

    key=${UREPO_GPG_SIGN_KEY:-$UREPO_ROOT/keys/rpm.key}
    [ -r "$key" ] || die "cannot read signing key: $key"
    arch=${UREPO_RPM_ARCH:-x86_64}
    work=$UREPO_ROOT/builddir/arch
    srcpkgs_dir=$UREPO_ROOT/arch/srcpkgs

    mkdir -p $work

    for pkg do
         info "Prepear $pkg for build"
         pkg_dir=$srcpkgs_dir/$pkg

         cd $pkg_dir

         info "Building $pkg"
         makepkg -s PKGDEST=$work/x86_64
    done
    create_repo
}

check_depenth() {
    require pacman
    require makepkg
    require gpg
    require repo-add
}


create_repo() {
    local REPO_DIR=$work/$arch
    local TMP_GPG=$work/gpg
    local RPM_FILES=($REPO_DIR/*.rpm)

    if [ ! -d $TMP_GPG ]; then
    mkdir -p $TMP_GPG
    gpg --homedir $TMP_GPG --import $key
    fi
    mkdir -p $REPO_DIR
    repo-add -p -R $work/x86_64/universalrepository.db.tar.gz $work/x86_64/*.tar.zst
    mv $work/x86_64/universalrepository.db.tar.gz $work/x86_64/universalrepository.db
    mv $work/x86_64/universalrepository.files.tar.gz $work/x86_64/universalrepository.files
}

