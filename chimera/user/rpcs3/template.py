pkgname = "rpcs3"
pkgver = "0.0.43"
pkgrel = 0
archs = ["aarch64", "x86_64"]
build_style = "cmake"
configure_args = [
    "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
    "-DCMAKE_BUILD_TYPE=Release",
    "-DUSE_NATIVE_INSTRUCTIONS=OFF",
    "-DWITH_LLVM=ON",
    "-DBUILD_LLVM=OFF",
    "-DSTATIC_LINK_LLVM=OFF",
    "-DLLVM_DIR=/usr/lib/cmake/llvm",
    "-DUSE_LTO=OFF",
    "-DDISABLE_LTO=ON",
    "-DBUILD_RPCS3_TESTS=OFF",
    "-DUSE_SYSTEM_CURL=ON",
    "-DUSE_SYSTEM_FFMPEG=ON",
    "-DUSE_SYSTEM_GLSLANG=ON",
    "-DUSE_SYSTEM_HIDAPI=ON",
    "-DUSE_SYSTEM_LIBPNG=ON",
    "-DUSE_SYSTEM_LIBUSB=ON",
    "-DUSE_SYSTEM_MINIUPNPC=ON",
    "-DUSE_SYSTEM_OPENAL=ON",
    "-DUSE_SYSTEM_OPENCV=ON",
    "-DUSE_SYSTEM_PROTOBUF=ON",
    "-DUSE_SYSTEM_PUGIXML=ON",
    "-DUSE_SYSTEM_RTMIDI=ON",
    "-DUSE_SYSTEM_SDL=ON",
    "-DUSE_SYSTEM_ZLIB=ON",
    "-DUSE_SYSTEM_ZSTD=ON",
    "-DOpenGL_GL_PREFERENCE=LEGACY",
]
hostmakedepends = [
    "cmake",
    "git",
    "glslang-progs",
    "ninja",
    "pkgconf",
    "protobuf",
]
makedepends = [
    "alsa-lib-devel",
    "curl-devel",
    "ffmpeg-devel",
    "glew-devel",
    "glslang-devel",
    "glu-devel",
    "hidapi-devel",
    "libevdev-devel",
    "libpng-devel",
    "libpulse-devel",
    "libx11-devel",
    "libxkbcommon-devel",
    "libxrandr-devel",
    "llvm-devel",
    "mesa-devel",
    "miniupnpc-devel",
    "openal-soft-devel",
    "opencv-devel",
    "protobuf-devel",
    "pugixml-devel",
    "qt6-qtbase-private-devel",
    "qt6-qtmultimedia-devel",
    "qt6-qtsvg-devel",
    "rtmidi-devel",
    "sdl3-devel",
    "spirv-tools-devel",
    "udev-devel",
    "vulkan-headers",
    "vulkan-loader-devel",
    "wayland-devel",
    "zlib-ng-compat-devel",
    "zstd-devel",
]
pkgdesc = "Sony PlayStation 3 emulator and debugger"
license = "GPL-2.0-only"
url = "https://rpcs3.net"
tool_flags = {
    "CXXFLAGS": ["-D_DEFAULT_SOURCE"],
}
# upstream rejects LTO, tests disabled for URepo
options = ["!check", "!lto"]


def fetch(self):
    self.do(
        "git",
        "clone",
        "--depth=1",
        "--branch",
        f"v{pkgver}",
        "--filter=blob:none",
        "https://github.com/RPCS3/rpcs3.git",
        ".",
    )
    self.do(
        "git",
        "submodule",
        "update",
        "--init",
        "--depth=1",
        f"--jobs={self.conf_jobs}",
        "--",
        "3rdparty/FAudio",
        "3rdparty/GPUOpen/VulkanMemoryAllocator",
        "3rdparty/SoundTouch/soundtouch",
        "3rdparty/asmjit/asmjit",
        "3rdparty/cubeb/cubeb",
        "3rdparty/discord-rpc/discord-rpc",
        "3rdparty/feralinteractive/feralinteractive",
        "3rdparty/fusion/fusion",
        "3rdparty/stblib/stb",
        "3rdparty/wolfssl/wolfssl",
        "3rdparty/yaml-cpp/yaml-cpp",
    )


def extract(self):
    pass


def post_install(self):
    self.uninstall("usr/share/rpcs3/test")
