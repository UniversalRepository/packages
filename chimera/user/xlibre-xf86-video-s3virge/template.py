pkgname = "xlibre-xf86-video-s3virge"
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
provides = [self.with_pkgver("xserver-xorg-video-s3virge")]
pkgdesc = "XLibre s3virge video driver"
license = "X11"
url = "https://github.com/X11Libre/xf86-video-s3virge"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "eee7cf3dc9859e037dfa3bf82cc14cdbea4ccdf7813bd0f59a8a837886d68943"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
