pkgname = "xlibre-xf86-video-i740"
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
provides = [self.with_pkgver("xserver-xorg-video-i740")]
pkgdesc = "XLibre i740 video driver"
license = "X11"
url = "https://github.com/X11Libre/xf86-video-i740"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "dd797c5eae9cc74a099c695c28bef951e45ecc06effab672fb9b805c2725af5f"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
