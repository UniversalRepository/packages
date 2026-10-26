pkgname = "xlibre-xf86-input-evdev"
pkgver = "25.0.0"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libevdev-devel",
    "mtdev-devel",
    "udev-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-input~26!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-input-evdev")]
pkgdesc = "XLibre evdev input driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-input-evdev"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "c810cc2d4ba63ee917f40b12e8e09c3e046653badcaace6897561dd3087944e8"


def post_install(self):
    self.install_license("COPYING")


@subpackage("xlibre-xf86-input-evdev-devel")
def _(self):
    self.provides = [self.with_pkgver("xserver-xorg-input-evdev-devel")]
    return self.default_devel()
