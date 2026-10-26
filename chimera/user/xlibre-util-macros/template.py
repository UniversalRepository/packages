pkgname = "xlibre-util-macros"
pkgver = "1.20.2"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf"]
provides = [self.with_pkgver("xorg-util-macros")]
pkgdesc = "XLibre autotools macros"
license = "MIT"
url = "https://github.com/X11Libre/mirror.fdo.xorg-macros"
source = f"{url}/archive/refs/tags/util-macros-{pkgver}.tar.gz"
sha256 = "43f870d7a42e562e0a3acbab41e9d94af338d5c617966ee7423f1039f3507c62"
options = ["!scanrundeps"]


def post_install(self):
    self.install_license("COPYING")
