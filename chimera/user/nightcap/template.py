pkgname = "nightcap"
pkgver = "0.5.0"
pkgrel = 0
archs = ["x86_64"]
build_style = "cmake"
configure_args = [
    "-DBUILD_TESTING=OFF",
    "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
    "-DMOCKTAIL_BUILD_FREEBSD_SOCKET_HELPER=OFF",
    "-DMOCKTAIL_DEFAULT_COMPATIBILITY_MANIFEST=/usr/share/mocktail/metadata/roblox_compatibility.json",
    "-DMOCKTAIL_DEFAULT_SIGNING_TRUST_MANIFEST=/usr/share/mocktail/metadata/roblox_signing_certificates.json",
]
hostmakedepends = ["cmake", "git", "ninja", "pkgconf"]
makedepends = [
    "capstone-devel",
    "curl-devel",
    "elfutils-devel",
    "ffmpeg-devel",
    "fontconfig-devel",
    "glib-devel",
    "gtk4-devel",
    "libadwaita-devel",
    "libglvnd-devel",
    "libplacebo-devel",
    "libpng-devel",
    "libsecret-devel",
    "libyaml-devel",
    "linux-headers",
    "minizip-devel",
    "nlohmann-json",
    "openssl3-devel",
    "sdl3-devel",
    "sdl3_ttf-devel",
    "utf8proc-devel",
    "vulkan-loader-devel",
    "webkitgtk4-devel",
    "zlib-ng-compat-devel",
]
depends = [
    "ca-certificates",
    "hicolor-icon-theme",
    "libglvnd",
    "so:libavcodec.so.62!ffmpeg-avcodec-libs",
    "so:libavutil.so.60!ffmpeg-avutil-libs",
    "vulkan-loader",
    "xdg-utils",
]
pkgdesc = "Android Roblox compatibility runtime with desktop improvements"
license = "Apache-2.0"
url = "https://github.com/CoderDayton/nightcap"
hardening = ["!cfi", "!vis"]
# tests fetch Google Test
options = ["!check", "!lto"]


def fetch(self):
    self.do(
        "git",
        "clone",
        "--depth=1",
        "--branch",
        f"v{pkgver}",
        "--recurse-submodules",
        "--shallow-submodules",
        url + ".git",
        ".",
    )


def extract(self):
    pass


def post_install(self):
    self.install_license("LICENSE")
    self.install_license(
        "third_party/libjnivm/LICENSE", name="LICENSE.libjnivm"
    )
