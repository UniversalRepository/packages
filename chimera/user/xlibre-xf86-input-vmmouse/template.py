pkgname = "xlibre-xf86-input-vmmouse"
pkgver = "25.0.0"
pkgrel = 0
archs = ["x86_64"]
build_style = "gnu_configure"
configure_args = ["--with-udev-rules-dir=/usr/lib/udev/rules.d"]
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = ["udev-devel", "xlibre-xorgproto", "xlibre-xserver-devel"]
depends = ["virtual:xlibre-abi-input~26!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-input-vmmouse")]
pkgdesc = "XLibre vmmouse input driver"
license = "MIT AND X11"
url = "https://github.com/X11Libre/xf86-input-vmmouse"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "41c760d547989d0b120b76e299c2b2611f13fb063838fb6c3fa7fe26eb756fbe"


def post_install(self):
    self.install_license("COPYING")
