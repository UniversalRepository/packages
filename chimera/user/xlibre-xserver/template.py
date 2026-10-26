pkgname = "xlibre-xserver"
pkgver = "25.2.2"
pkgrel = 0
build_style = "meson"
configure_args = [
    "-Dxorg=true",
    "-Dxnest=true",
    "-Dxephyr=true",
    "-Dxvfb=true",
    "-Dipv6=true",
    "-Dxcsecurity=true",
    "-Dglamor=true",
    "-Ddri2=true",
    "-Ddri3=true",
    "-Dglx=true",
    "-Dseatd_libseat=true",
    "-Dsystemd_logind=false",
    "-Dsystemd_notify=false",
    "-Dsuid_wrapper=true",
    "-Dudev=true",
    "-Dlinux_acpi=true",
    "-Dlinux_apm=false",
    "-Dhal=false",
    "-Dxkb_dir=/usr/share/X11/xkb",
    "-Dxkb_output_dir=/var/lib/xkb",
    "-Ddefault_font_path=/usr/share/fonts/misc,/usr/share/fonts/TTF,/usr/share/fonts/Type1",
    "-Dlegacy_nvidia_padding=false",
]
hostmakedepends = ["flex", "meson", "pkgconf", "xkbcomp"]
makedepends = [
    "dbus-devel",
    "font-util-devel",
    "libdrm-devel",
    "libepoxy-devel",
    "libpciaccess-devel",
    "libseat-devel",
    "libtirpc-devel",
    "libxcb-devel",
    "libxcvt-devel",
    "libxfont2-devel",
    "libxkbfile-devel",
    "libxkbui-devel",
    "libxrender-devel",
    "libxres-devel",
    "libxshmfence-devel",
    "libxtst-devel",
    "libxv-devel",
    "libxxf86dga-devel",
    "mesa-devel",
    "mesa-gbm-devel",
    "nettle-devel",
    "openssl3-devel",
    "pixman-devel",
    "udev-devel",
    "xcb-util-devel",
    "xcb-util-image-devel",
    "xcb-util-keysyms-devel",
    "xcb-util-renderutil-devel",
    "xcb-util-wm-devel",
    "xkbcomp-devel",
    "xlibre-xorgproto",
    "xtrans",
]
checkdepends = ["xkeyboard-config"]
depends = [
    "so:libEGL.so.1!mesa-egl-libs",
    "xkeyboard-config",
    "xserver-xorg-protocol>=20180227",
    self.with_pkgver("xlibre-xserver-common"),
]
provides = [
    self.with_pkgver("xserver-xorg-core"),
    "xlibre-abi-extension=11.0",
    "xlibre-abi-input=26.0",
    "xlibre-abi-video=28.0",
]
pkgdesc = "XLibre X server"
license = "MIT AND BSD-3-Clause"
url = "https://github.com/X11Libre/xserver"
source = f"{url}/archive/refs/tags/xlibre-xserver-{pkgver}.tar.gz"
sha256 = "3c1f07f4b5f8a483473097be4b964ee97a2b92adde9de6c0d8d9d7217a382810"
tool_flags = {
    "CFLAGS": ["-D_GNU_SOURCE", "-D__uid_t=uid_t", "-D__gid_t=gid_t"],
    "LDFLAGS": ["-Wl,-z,lazy"],
}
file_modes = {"usr/lib/Xorg.wrap": ("root", "root", 0o4755)}
hardening = ["!int"]
# X server tests require a live display
options = ["!check"]

if self.profile.arch == "x86_64":
    configure_args += ["-Dint10=x86emu"]
else:
    configure_args += ["-Dint10=false"]


def post_install(self):
    self.install_license("COPYING")
    self.install_license("COPYING", pkgname="xlibre-xserver-xvfb")
    self.chmod(self.destdir / "usr/lib/Xorg.wrap", mode=0o4755)
    self.uninstall("etc/X11/xorg.conf.d/10-nvidia.conf.debian")
    self.uninstall("etc/X11/xorg.conf.d/10-nvidia-modules.conf.debian")
    self.uninstall("usr/lib/xorg/protocol.txt")
    self.install_bin(self.files_path / "xvfb-run")
    self.install_man(self.files_path / "xvfb-run.1")


@subpackage("xlibre-xserver-xnest")
def _(self):
    self.pkgdesc = "XLibre nested X server"
    self.provides = [self.with_pkgver("xserver-xorg-xnest")]
    return ["usr/bin/Xnest", "usr/share/man/man1/Xnest.1"]


@subpackage("xlibre-xserver-xephyr")
def _(self):
    self.pkgdesc = "XLibre server outputting to an existing X display"
    self.provides = [self.with_pkgver("xserver-xorg-xephyr")]
    return ["usr/bin/Xephyr", "usr/share/man/man1/Xephyr.1"]


@subpackage("xlibre-xserver-xvfb")
def _(self):
    self.pkgdesc = "XLibre virtual framebuffer X server"
    self.license = "MIT AND BSD-3-Clause AND GPL-2.0-or-later"
    self.depends += ["xkeyboard-config", "xauth", "ugetopt"]
    self.provides = [self.with_pkgver("xserver-xorg-xvfb")]
    return [
        "usr/bin/Xvfb",
        "usr/bin/xvfb-run",
        "usr/share/licenses/xlibre-xserver-xvfb",
        "usr/share/man/man1/Xvfb.1",
        "usr/share/man/man1/xvfb-run.1",
    ]


@subpackage("xlibre-xserver-common")
def _(self):
    self.subdesc = "common files"
    self.options = ["!autosplit"]
    return ["usr/share/man/man1/Xserver.1"]


@subpackage("xlibre-xserver-devel")
def _(self):
    self.depends += [
        "!xserver-xorg-devel",
        "libpciaccess-devel",
        "libxcb-devel",
        "libxfont2-devel",
        "libxi-devel",
        "libxkbfile-devel",
        "libxrandr-devel",
        "libxrender-devel",
        "libxshmfence-devel",
        "xlibre-xorgproto",
        "xtrans",
    ]
    return self.default_devel()
