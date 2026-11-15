pkgname = "rlottie"
pkgver = "0.2"
pkgrel = 0
build_style = "meson"
configure_args = [
    "-Ddefault_library=shared",
    "-Dexample=false",
    "-Dmodule=false",
    "-Dtest=false",
]
hostmakedepends = ["meson", "pkgconf"]
pkgdesc = "Library for rendering Lottie animations"
license = "MIT"
url = "https://github.com/Samsung/rlottie"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "030ccbc270f144b4f3519fb3b86e20dd79fb48d5d55e57f950f12bab9b65216a"
# might not work in CI
options = ["!check", "sanruntime"]


def post_install(self):
    self.install_license("COPYING")


@subpackage("rlottie-devel")
def _(self):
    return self.default_devel()
