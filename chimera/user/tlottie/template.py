pkgname = "tlottie"
pkgver = "1.0.6"
pkgrel = 0
build_style = "cargo"
make_env = {"CARGO_PROFILE_RELEASE_LTO": "false"}
make_check_args = [
    "--release",
    "--lib",
    "--features=c-api",
    "--locked",
    "--",
    "--test-threads=1",
    "--skip=dos::animated_repeater_product_stays_bounded",
    "--skip=dos::clipped_dashed_round_join_zigzag_stays_bounded",
    "--skip=dos::compounding_repeaters_are_rejected",
    "--skip=dos::nested_track_matte_target_surfaces_stay_bounded",
    "--skip=dos::renderer_rejects_large_canvas_before_allocating_fallback",
]
hostmakedepends = ["cargo-auditable"]
makedepends = ["rust-std"]
pkgdesc = "Lottie animation renderer with a static C API"
license = "MIT"
url = "https://github.com/dkaraush/tlottie"
source = f"{url}/archive/v{pkgver}.tar.gz"
sha256 = "a85dd1a8f62ca85248af380d5eee6f32e84b29c45134615b23355207ccb90359"
options = ["!lto"]


def build(self):
    self.cargo.build(
        ["--locked", "--lib", "--features=c-api", "--crate-type=staticlib"],
        command="rustc",
    )


def install(self):
    from cbuild.util import cargo

    self.install_lib(cargo.target_path(self, "libtlottie.a"))
    self.install_file("include/tlottie.h", "usr/include/tlottie")
    self.install_license("LICENSE")
