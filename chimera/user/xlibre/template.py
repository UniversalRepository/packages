pkgname = "xlibre"
pkgver = "25.1.0"
pkgrel = 0
build_style = "meta"
depends = [
    "xlibre-apps",
    "xlibre-input-drivers",
    "xlibre-minimal",
    "xlibre-video-drivers",
]
provides = [self.with_pkgver("xserver-xorg")]
pkgdesc = "Complete XLibre desktop installation"
license = "custom:meta"
url = "https://github.com/X11Libre/xserver"
