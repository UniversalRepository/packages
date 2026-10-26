pkgname = "xlibre-xf86-video-mga"
pkgver = "25.0.0"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libdrm-devel",
    "libpciaccess-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-video~28!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-video-mga")]
pkgdesc = "XLibre mga video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-mga"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "af619a36e6b7c8f951e3c1329889bbacd8864ed8dea32d306ab8cfd748b24ad4"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
