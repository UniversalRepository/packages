pkgname = "xlibre-xf86-video-mach64"
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
provides = [self.with_pkgver("xserver-xorg-video-mach64")]
pkgdesc = "XLibre mach64 video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-mach64"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "8118cd54d51163fe9c6246a4f02a9457d5696167a469607fd9539a02b3a2e9af"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
