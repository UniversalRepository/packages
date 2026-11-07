pkgname = "ayugram-desktop"
pkgver = "7.2.9"
pkgrel = 0
archs = ["aarch64", "loongarch64", "ppc64le", "riscv64", "x86_64"]
build_style = "cmake"
configure_args = [
    "-DBUILD_SHARED_LIBS=OFF",
    "-DDESKTOP_APP_USE_PACKAGED=ON",
    "-DTDESKTOP_API_ID=209235",
    "-DTDESKTOP_API_HASH=169ee702e1df4b6e66d80311db36cc43",
    "-DDESKTOP_APP_DISABLE_CRASH_REPORTS=ON",
    "-DWaylandScanner_EXECUTABLE=/usr/bin/wayland-scanner",
    "-DQT_HOST_PATH=/usr",
    "-DQSB_EXECUTABLE=/usr/lib/qt6/bin/qsb",
]
hostmakedepends = [
    "cmake",
    "extra-cmake-modules",
    "glib-devel",
    "gobject-introspection",
    "gperf",
    "ninja",
    "pkgconf",
    "protobuf",
    "python",
    "qt6-qtbase",
    "qt6-qtdeclarative",
    "qt6-qtshadertools",
    "wayland-progs",
]
makedepends = [
    "ada-devel",
    "alsa-lib-devel",
    "boost-devel",
    "ffmpeg-devel",
    "fmt-devel",
    "glib-devel",
    "hunspell-devel",
    "jemalloc-devel",
    "kcoreaddons-devel",
    "libavif-devel",
    "libdbusmenu-devel",
    "libdispatch-devel",
    "libfido2-devel",
    "libjpeg-turbo-devel",
    "libjxl-devel",
    "libpulse-devel",
    "libva-devel",
    "libxcb-devel",
    "lz4-devel",
    "mesa-devel",
    "minizip-devel",
    "openal-soft-devel",
    "openssl3-devel",
    "opus-devel",
    "protobuf-devel",
    "qt6-qt5compat-devel",
    "qt6-qtbase-devel",
    "qt6-qtbase-private-devel",
    "qt6-qtdeclarative-devel",
    "qt6-qtshadertools-devel",
    "qt6-qtsvg-devel",
    "qt6-qtwayland-devel",
    "rapidjson",
    "rnnoise-devel",
    "tg_owt-static",
    "tlottie",
    "xcb-util-keysyms-devel",
    "xxhash-devel",
    "xz-devel",
    "zlib-ng-compat-devel",
]
depends = ["fonts-opensans-ttf", "qt6-qtimageformats", "webkitgtk4"]
pkgdesc = "Telegram desktop client with additional customization features"
license = "GPL-3.0-or-later"
url = "https://github.com/AyuGram/AyuGramDesktop"
source = [
    f"{url}/releases/download/v{pkgver}/AyuGramDesktop-{pkgver}-full.tar.gz",
    "https://github.com/tdlib/td/archive/022d60202e446ad1287b9fb68e687c8a0760788b.tar.gz",
]
source_paths = [".", "tde2e"]
sha256 = [
    "ead2665a32f38277e76d3041a5b780100afa0d87b7b1440c1278c5229936a842",
    "b0837cd880a6de8d45abdfd5024fe0f042c100eb5f241a5f185ba65579acfc32",
]
debug_level = 1
hardening = ["!int"]
options = ["!cross"]


def pre_configure(self):
    from cbuild.util import cmake

    with self.stamp("tde2e_configure") as stamp:
        stamp.check()
        cmake.configure(
            self,
            build_dir="tde2e/out/Release",
            cmake_dir="tde2e",
            extra_args=[
                "-DBUILD_SHARED_LIBS=OFF",
                "-DBUILD_TESTING=OFF",
                "-DTD_E2E_ONLY=ON",
                "-DTDUTILS_MIME_TYPE=OFF",
                "-DTD_INSTALL_SHARED_LIBRARIES=OFF",
            ],
        )

    with self.stamp("tde2e_build") as stamp:
        stamp.check()
        cmake.build(self, "tde2e/out/Release", ["--target", "tde2e"])
