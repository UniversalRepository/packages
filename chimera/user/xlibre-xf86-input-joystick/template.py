pkgname = "xlibre-xf86-input-joystick"
pkgver = "25.0.0"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = ["linux-headers", "xlibre-xorgproto", "xlibre-xserver-devel"]
depends = ["virtual:xlibre-abi-input~26!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-input-joystick")]
pkgdesc = "XLibre joystick input driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-input-joystick"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "af821e11477d8c1bdb08ee2cbadfd556159d42b394699b2c980aa5c818441520"


def post_install(self):
    self.install_license("COPYING")


@subpackage("xlibre-xf86-input-joystick-devel")
def _(self):
    self.provides = [self.with_pkgver("xserver-xorg-input-joystick-devel")]
    return self.default_devel()
