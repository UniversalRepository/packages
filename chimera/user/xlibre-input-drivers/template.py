pkgname = "xlibre-input-drivers"
pkgver = "25.0.0"
pkgrel = 0
build_style = "meta"
depends = [
    "xlibre-xf86-input-evdev",
    "xlibre-xf86-input-libinput",
    "xlibre-xf86-input-synaptics",
    "xlibre-xf86-input-wacom",
]
pkgdesc = "XLibre input drivers"
license = "custom:meta"
url = "https://github.com/X11Libre/xserver"

if self.profile.arch == "x86_64":
    depends += ["xlibre-xf86-input-vmmouse"]
