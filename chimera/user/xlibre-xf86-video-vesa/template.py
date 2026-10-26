pkgname = "xlibre-xf86-video-vesa"
pkgver = "25.0.0"
pkgrel = 0
archs = ["x86_64"]
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libpciaccess-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-video~28!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-video-vesa")]
pkgdesc = "XLibre vesa video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-vesa"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "8d517cbd93a42b202cf624e8f56b646aa5efacd44e001f809fea6c5c08f8dfe7"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
