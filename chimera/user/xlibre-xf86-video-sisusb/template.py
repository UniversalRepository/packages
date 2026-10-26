pkgname = "xlibre-xf86-video-sisusb"
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
provides = [self.with_pkgver("xserver-xorg-video-sisusb")]
pkgdesc = "XLibre sisusb video driver"
license = "BSD-3-Clause"
url = "https://github.com/X11Libre/xf86-video-sisusb"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "470d8cb446797efb133e1a54bf1c1048804cd70843b3fce13700c0b01deeca4d"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
