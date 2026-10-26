pkgname = "xlibre-xf86-video-vmware"
pkgver = "25.0.0"
pkgrel = 0
archs = ["x86_64"]
build_style = "gnu_configure"
configure_args = ["--disable-vmwgfx"]
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libdrm-devel",
    "libpciaccess-devel",
    "libx11-devel",
    "libxext-devel",
    "udev-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-video~28!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-video-vmware")]
pkgdesc = "XLibre vmware video driver"
license = "MIT AND X11"
url = "https://github.com/X11Libre/xf86-video-vmware"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "5aabf5932fe071c21f621a5bfa5bc93523cbd6ef10cef5f3ecf89bf0ea66bbb4"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
