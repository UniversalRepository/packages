pkgname = "xlibre-xf86-video-fbdev"
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
provides = [self.with_pkgver("xserver-xorg-video-fbdev")]
pkgdesc = "XLibre fbdev video driver"
license = "X11"
url = "https://github.com/X11Libre/xf86-video-fbdev"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "638ffdbb2e43a9a2b76883efde645a7123ff348212b7722fe970e3949efb9808"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
