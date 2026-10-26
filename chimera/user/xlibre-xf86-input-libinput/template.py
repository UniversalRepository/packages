pkgname = "xlibre-xf86-input-libinput"
pkgver = "25.0.1"
pkgrel = 0
build_style = "meson"
hostmakedepends = ["meson", "pkgconf"]
makedepends = ["libinput-devel", "xlibre-xorgproto", "xlibre-xserver-devel"]
depends = ["virtual:xlibre-abi-input~26!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-input-libinput")]
provides += [self.with_pkgver("xserver-xorg-input-driver")]
pkgdesc = "XLibre libinput input driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-input-libinput"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "d7d9246b6f9a03459a5b603b726aa4e4c0ec8ea669fff2f38976bc81eec96a44"


def post_install(self):
    self.install_license("COPYING")


@subpackage("xlibre-xf86-input-libinput-devel")
def _(self):
    self.provides = [self.with_pkgver("xserver-xorg-input-libinput-devel")]
    return self.default_devel()
