pkgname = "cressida"
pkgver = "0.3.0"
pkgrel = 0
build_style = "meson"
configure_args = [
    "-Dtests=disabled",
    "-Demoji_font=/usr/share/fonts/noto/NotoColorEmoji.ttf",
]
hostmakedepends = [
    "meson",
    "pkgconf",
    "python",
    "wayland-progs",
    "xdg-utils",
]
makedepends = [
    "cairo-devel",
    "curl-devel",
    "ffmpeg-devel",
    "fontconfig-devel",
    "freetype-devel",
    "glib-devel",
    "harfbuzz-devel",
    "libglvnd-devel",
    "libjxl-devel",
    "libpulse-devel",
    "librsvg-devel",
    "libsecret-devel",
    "libsodium-devel",
    "libwebp-devel",
    "libxkbcommon-devel",
    "md4c-devel",
    "mpv-devel",
    "nlohmann-json",
    "openssl3-devel",
    "opus-devel",
    "pango-devel",
    "pipewire-devel",
    "qrencode-devel",
    "rlottie-devel",
    "stb",
    "tomlplusplus-devel",
    "wayland-devel",
    "wayland-protocols",
    "zstd-devel",
]
depends = [
    "ca-certificates",
    "fonts-noto-emoji-ttf",
    "hicolor-icon-theme",
    "shared-mime-info",
    "xdg-utils",
]
pkgdesc = "Native Discord client for Wayland"
license = "MIT"
url = "https://github.com/Ly-sec/Cressida"
source = f"{url}/archive/v{pkgver}.tar.gz"
sha256 = "a029f850f851083a2bfd70b8d9cd442692d2ef3fdfd317afdfa461e4381f669d"
# may not run in CI
options = ["!check"]

@subpackage("cressida-devel")
def _(self):
    return self.default_devel()
