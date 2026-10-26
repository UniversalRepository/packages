pkgname = "xlibre-xf86-video-openchrome"
pkgver = "25.0.0"
pkgrel = 0
archs = ["x86_64"]
build_style = "gnu_configure"
configure_args = ["--disable-xvmc"]
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libdrm-devel",
    "libpciaccess-devel",
    "libx11-devel",
    "libxext-devel",
    "mesa-devel",
    "udev-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-video~28!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-video-openchrome")]
pkgdesc = "XLibre openchrome video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-openchrome"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "8e14401a2160c6a7174b09875b4f87d2ad92cecad51e4762fc8739a536cb835a"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
