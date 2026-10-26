pkgname = "xlibre-xf86-video-i128"
pkgver = "25.0.0"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libpciaccess-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-video~28!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-video-i128")]
pkgdesc = "XLibre i128 video driver"
license = "X11"
url = "https://github.com/X11Libre/xf86-video-i128"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "8429acab3df07ea0ea8d1f6d2584abd6bfe877c533cf21adebad95ef9d799b4c"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
