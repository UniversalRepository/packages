pkgname = "xlibre-xf86-video-intel"
pkgver = "25.0.2"
pkgrel = 0
archs = ["x86_64"]
build_style = "gnu_configure"
configure_args = [
    "--disable-backlight-helper",
    "--disable-selective-werror",
    "--disable-xvmc",
    "--disable-tools",
]
hostmakedepends = ["automake", "libtool", "pkgconf", "xlibre-util-macros"]
makedepends = [
    "libdrm-devel",
    "libpciaccess-devel",
    "libx11-devel",
    "libxcb-devel",
    "libxcomposite-devel",
    "libxdamage-devel",
    "libxext-devel",
    "libxfixes-devel",
    "libxrandr-devel",
    "libxrender-devel",
    "libxshmfence-devel",
    "libxxf86vm-devel",
    "udev-devel",
    "xlibre-xorgproto",
    "xlibre-xserver-devel",
]
depends = ["virtual:xlibre-abi-video~28!xlibre-xserver"]
provides = [self.with_pkgver("xserver-xorg-video-intel")]
pkgdesc = "XLibre intel video driver"
license = "MIT"
url = "https://github.com/X11Libre/xf86-video-intel"
source = f"{url}/archive/refs/tags/{pkgname}-{pkgver}.tar.gz"
sha256 = "e4513cf871374cc5df4d0ae5dcd2787539c38801295ab5a9b3470cf0dd193a43"
tool_flags = {"LDFLAGS": ["-Wl,-z,lazy"]}
hardening = ["!int"]


def post_install(self):
    self.install_license("COPYING")
