pkgname = "xlibre-xf86-video-dummy"
pkgver = "25.0.0"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = ["xlibre-xorgproto", "xlibre-xserver-devel"]
depends = ["virtual:xlibre-abi-video~28!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-video-dummy")]
pkgdesc = "XLibre dummy video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-dummy"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "b56e610705cd3d4d86422a11c6b0d93357e4d4749a05178a85fd250301d357b9"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
