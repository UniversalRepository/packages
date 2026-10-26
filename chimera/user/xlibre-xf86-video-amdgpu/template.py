pkgname = "xlibre-xf86-video-amdgpu"
pkgver = "25.0.3"
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
provides = [self.with_pkgver("xserver-xorg-video-amdgpu")]
pkgdesc = "XLibre amdgpu video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-amdgpu"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "7aee2340914cf84d2ce4ab86ed7866f7b2876090e7f63fe9f5d05e2fb158e805"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
