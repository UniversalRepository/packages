pkgname = "xlibre-xf86-input-void"
pkgver = "25.0.0"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = ["xlibre-xorgproto", "xlibre-xserver-devel"]
depends = ["virtual:xlibre-abi-input~26!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-input-void")]
pkgdesc = "XLibre void input driver"
license = "MIT AND X11"
url = "https://github.com/X11Libre/xf86-input-void"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "2b242b55e429c25e31ca884dedf43bb60be4dbdd0a7ff015f10fa23cd6e08064"


def post_install(self):
    self.install_license("COPYING")
