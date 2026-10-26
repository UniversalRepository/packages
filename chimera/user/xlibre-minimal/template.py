pkgname = "xlibre-minimal"
pkgver = "25.1.0"
pkgrel = 0
build_style = "meta"
depends = [
    "fonts-xorg",
    "xauth",
    "xinit",
    "xlibre-xf86-input-libinput",
    "xlibre-xserver",
]
provides = [self.with_pkgver("xserver-xorg-minimal")]
pkgdesc = "Minimal XLibre desktop installation"
license = "custom:meta"
url = "https://github.com/X11Libre/xserver"
