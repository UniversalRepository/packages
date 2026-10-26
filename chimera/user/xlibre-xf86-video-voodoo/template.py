pkgname = "xlibre-xf86-video-voodoo"
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
provides = [self.with_pkgver("xserver-xorg-video-voodoo")]
pkgdesc = "XLibre voodoo video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-voodoo"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "13d94cd94037ab950cf81a787fc9b9d87de0d2ec69ff5f4623278ea2fd27a2e6"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
