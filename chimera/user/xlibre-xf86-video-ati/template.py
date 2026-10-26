pkgname = "xlibre-xf86-video-ati"
pkgver = "25.0.1"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libdrm-devel",
    "libpciaccess-devel",
    "mesa-devel",
    "mesa-gbm-devel",
    "udev-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-video~28!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-video-ati")]
pkgdesc = "XLibre ati video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-ati"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "35c96222fdbce8112f3a44b63d098a8a59c5950265ccf400561e49b8010fb0f6"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
