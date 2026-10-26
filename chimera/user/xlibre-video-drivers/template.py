pkgname = "xlibre-video-drivers"
pkgver = "25.0.0"
pkgrel = 0
build_style = "meta"
depends = [
    "xlibre-xf86-video-amdgpu",
    "xlibre-xf86-video-ati",
    "xlibre-xf86-video-dummy",
    "xlibre-xf86-video-fbdev",
    "xlibre-xf86-video-nouveau",
]
pkgdesc = "XLibre video drivers"
license = "custom:meta"
url = "https://github.com/X11Libre/xserver"

if self.profile.arch == "x86_64":
    depends += ["xlibre-xf86-video-vesa", "xlibre-xf86-video-vmware"]
