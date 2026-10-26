pkgname = "xlibre-xorgproto"
pkgver = "2025.1"
pkgrel = 0
build_style = "meson"
configure_args = ["-Dlegacy=true"]
hostmakedepends = ["meson", "pkgconf"]
provides = [self.with_pkgver("xorgproto")]
pkgdesc = "XLibre X11 protocol headers"
license = "MIT"
url = "https://github.com/X11Libre/mirror.fdo.xorgproto"
source = f"{url}/archive/refs/tags/xorgproto-{pkgver}.tar.gz"
sha256 = "185f272819d70adba383245995b99bce21e7b1f25bded669debbee1a519ad744"
options = ["!scanrundeps"]


def post_install(self):
    for f in self.cwd.glob("COPYING-*"):
        self.install_license(f)

    for os in ["apple", "windows"]:
        self.uninstall(f"usr/include/X11/extensions/{os}*", glob=True)
        self.uninstall(f"usr/share/licenses/{pkgname}/COPYING-{os}wmproto")
        self.uninstall(f"usr/share/pkgconfig/{os}wmproto.pc")

    self.uninstall("usr/include/X11/extensions/XKBgeom.h")
