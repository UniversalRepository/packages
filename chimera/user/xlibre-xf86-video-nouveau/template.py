pkgname = "xlibre-xf86-video-nouveau"
pkgver = "25.0.0"
pkgrel = 0
build_style = "gnu_configure"
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libdrm-devel",
    "libpciaccess-devel",
    "udev-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-video~28!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-video-nouveau")]
pkgdesc = "XLibre nouveau video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-nouveau"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "bc56f320ba6ce4d068351ac259cdb87571a05e03402afad02352bcb62be7b040"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    notices = []
    for path in sorted((self.cwd / "src").rglob("*")):
        if path.suffix not in {".c", ".h"}:
            continue
        text = path.read_text().lstrip()
        while text.startswith("/*"):
            notice, separator, text = text.partition("*/")
            if not separator:
                break
            notice += "*/\n"
            if "copyright" in notice.lower() and notice not in notices:
                notices.append(notice)
            text = text.lstrip()
    (self.cwd / "COPYING").write_text("\n".join(notices))
    self.install_license("COPYING")
