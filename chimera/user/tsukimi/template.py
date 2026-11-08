pkgname = "tsukimi"
pkgver = "26.10.1"
pkgrel = 0
build_style = "meson"
configure_args = ["-Dsandboxed-build=true"]
hostmakedepends = [
    "blueprint-compiler",
    "cargo",
    "cmake",
    "gettext",
    "glib-devel",
    "libxml2-progs",
    "meson",
    "pkgconf",
]
makedepends = [
    "dbus-devel",
    "glib-devel",
    "glycin-devel",
    "gst-plugins-bad-devel",
    "gst-plugins-base-devel",
    "gstreamer-devel",
    "gtk4-devel",
    "lcms2-devel",
    "libadwaita-devel",
    "libepoxy-devel",
    "libseccomp-devel",
    "mpv-devel",
    "openssl3-devel",
    "rust-std",
]
depends = [
    "ca-certificates",
    "glycin-loaders",
    "gst-plugins-base",
    "gst-plugins-good",
    "hicolor-icon-theme",
    "libepoxy",
]
checkdepends = ["appstream", "desktop-file-utils"]
pkgdesc = "Third-party Jellyfin client"
license = "GPL-3.0-or-later"
url = "https://github.com/tsukinaha/tsukimi"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "0f512eba652282366e51a8f928e1d8e7fb45bc833e5651ed5d16c081dda1c12f"
options = ["!cross"]


def prepare(self):
    from cbuild.util import cargo

    cargo.Cargo(self, wrksrc=".").vendor(["--locked"])


def init_build(self):
    from cbuild.util import cargo

    env = cargo.get_environment(self)
    del env["CARGO_BUILD_TARGET"]
    env["CARGO_NET_OFFLINE"] = "true"
    self.make_env.update(env)
