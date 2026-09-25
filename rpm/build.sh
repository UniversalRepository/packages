distro_build() {
	set -eu

	require rpm
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

	case "$ID" in
		fedora)
			for pkg do
				info "Building $pkg"

			done
			;;
		opensuse*|sles|ledet)
			for pkg do
				info "Building $pkg"
			done
			;;
	esac


}
