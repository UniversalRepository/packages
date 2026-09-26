distro_build() {
	set -eu

	require rpm
	require sudo
	require rpmbuild
	if [ ! -f /etc/os-release ]; then
		echo "Failed to find os-release file"
		exit 1
	fi
	source /etc/os-release
	case "$ID" in
		fedora)
			require dnf
			require spectools
			;;
		opensuse*|sles|ledet)
			require zypper
			require rpmdev-spectool
			;;
		*)
			error "I think you have unsupported rpm distro by UniversalRepository Cli"; exit 2
			;;
	esac
	key=${UREPO_RPM_SIGN_KEY:-$UREPO_ROOT/keys/rpm.key}
	[ -r "$key" ] || die "cannot read signing key: $key"

	work=$UREPO_ROOT/builddir/rpm
	srcpkgs_dir=$UREPO_ROOT/rpm/srcpkgs

	mkdir -p $work

	case "$ID" in
		fedora)
			for pkg do
				info "Prepear $pkg for build"
				pkg_dir=$srcpkgs_dir/$pkg
				cd $pkg_dir
				
				info "Downloading $pkg sources"
				spectools -g $pkg.spec
				info "Downloading $pkg BuildRequires"
				if [ "$EUID" -eq 0 ]; then
					dnf builddep -y $pkg.spec
				else
					warn "This action requires root access!"
					sudo dnf builddep -y $pkg.spec
				fi
				info "Building $pkg"
				rpmbuild \
				--define "_topdir $work" \
				--define "_sourcedir $pkg_dir" \
				--define "_specdir $pkg_dir" \
				--define "_srcrpmdir $work"\
				--define "_rpmdir $work" \
					-ba "$pkg.spec"
			done
			;;
		opensuse*|sles|ledet)
			for pkg do
				info "Prepear $pkg for build"
				pkg_dir=$srcpkgs_dir/$pkg
				cd $pkg_dir
				
				info "Downloading $pkg sources"
				rpmdev-spectool -g $pkg.spec
				info "Downloading $pkg BuildRequires"
				if [ "$EUID" -eq 0 ]; then
					zypper --non-interactive source-install --build-deps-only "$pkg.spec" || [ $? -eq 104 ]
				else
					warn "This action requires root access!"
					sudo zypper --non-interactive source-install --build-deps-only "$pkg.spec" || [ $? -eq 104 ]
				fi
				info "Building $pkg"
				rpmbuild \
				--define "_topdir $work" \
				--define "_sourcedir $pkg_dir" \
				--define "_specdir $pkg_dir" \
				--define "_srcrpmdir $work"\
				--define "_rpmdir $work" \
					-ba "$pkg.spec"
			done
			;;
	esac
}
