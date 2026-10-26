pkgname = "xlibre-xf86-input-elographics"
pkgver = "25.0.1"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = ["xlibre-xorgproto", "xlibre-xserver-devel"]
depends = ["virtual:xlibre-abi-input~26!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-input-elographics")]
pkgdesc = "XLibre elographics input driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-input-elographics"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "0c2a82881199a08ec6236e1338f7699ea42d82cad2fafc99e9869644e8240e9b"


def post_install(self):
    self.install_license("COPYING")
