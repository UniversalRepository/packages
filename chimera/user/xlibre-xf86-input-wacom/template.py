pkgname = "xlibre-xf86-input-wacom"
pkgver = "25.0.0"
pkgrel = 0
build_style = "meson"
configure_args = ["-Dwacom-gobject=disabled", "-Dunittests=disabled"]
hostmakedepends = ["meson", "pkgconf"]
makedepends = [
    "libx11-devel",
    "libxext-devel",
    "libxi-devel",
    "libxinerama-devel",
    "libxrandr-devel",
    "linux-headers",
    "udev-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-input~26!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-input-wacom")]
pkgdesc = "XLibre wacom input driver"
license = "GPL-2.0-or-later"
url = "https://github.com/X11Libre/xf86-input-wacom"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "12878547b271f4e59ecd5098f935d4c0bd4560d0c2a3a667385d916bc63d00af"
# unit tests need an X server
options = ["!check"]


def post_install(self):
    self.rm(self.destdir / "usr/lib/systemd", recursive=True)


@subpackage("xlibre-xf86-input-wacom-devel")
def _(self):
    self.provides = [self.with_pkgver("xserver-xorg-input-wacom-devel")]
    return self.default_devel()
