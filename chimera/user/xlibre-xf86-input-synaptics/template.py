pkgname = "xlibre-xf86-input-synaptics"
pkgver = "25.0.0"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libevdev-devel",
    "libx11-devel",
    "libxi-devel",
    "libxtst-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-input~26!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-input-synaptics")]
pkgdesc = "XLibre synaptics input driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-input-synaptics"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "fca6a16ed199505a27dc167e88722b4d45aa5f46e86561d6c6eee3d7a750a107"


def post_install(self):
    self.install_license("COPYING")


@subpackage("xlibre-xf86-input-synaptics-devel")
def _(self):
    self.provides = [self.with_pkgver("xserver-xorg-input-synaptics-devel")]
    return self.default_devel()
