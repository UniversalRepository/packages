# Contributing

All contributions are welcome. Follow the standard packaging guidelines for the respective distro where possible. Packages should be tested locally before being submitted.

## Local testing

Please test build all templates before opening a PR. See the [README](README.md#building-packages-natively) for build commands, package directories, and container setup.

Use the distro's own packaging guidelines and checks:

- **Void Linux:** Follow the [void-packages manual](https://github.com/void-linux/void-packages/blob/master/Manual.md). Templates should also pass [xlint](https://man.voidlinux.org/xlint).
- **Arch Linux:** Follow the [Arch packaging standards](https://wiki.archlinux.org/title/Arch_package_guidelines). Check dependencies and any split packages produced by the `PKGBUILD`.
- **Chimera Linux:** Follow the [cports packaging guidelines](https://github.com/chimera-linux/cports/blob/master/Packaging.md) and the checks provided by `cbuild`.

Please also test installing and running the resulting package. Even if templates compile, they should still follow the respective distro's packaging conventions.

If a package is known to not work on e.g musl or a particular architecture, add the appropriate restriction to its build definition. Mention what you tested in the PR, and anything you were unable to test.

## Packaging guidelines

As mentioned previously, follow distro conventions where possible, but here are some particular mentions:

- **A package is available for another distro:** You can contribute it for just one distro. It does not need to be available for every distro we support.
- **A package requires git submodules:** Include the required submodule sources using the distro's supported fetching methods. If downloading separate tarballs, keep their versions and checksums alongside the main source.
- **A package is in beta/unreleased:** This can be complex depending on the particular package, so we will work with you in an issue/PR to make it work.
- **A package is copied from elsewhere:** Keep the original attribution and include a link to where it came from in the PR. Check that the license allows us to redistribute it.
- **A package needs patches or additional files:** Keep these alongside its build definition, following the respective distro's directory layout. For Void, service files and other files installed by the template belong in `files/`.
- **A package is updated:** Update the version and source checksums, and reset the package revision/release where appropriate. If changing the packaging without updating the upstream version, bump the revision/release instead.
- **A package is a custom kernel:** It must be portable (no `-march=native` etc.). The same applies to other packages intended for distribution.
- **I want to build a package, but my device is too weak to build in reasonable time:** Open an issue and we will try to help.

You can open a Pull Request even if you don't have a finished template. Briefly explain what works, what doesn't, and include any relevant build logs.

If you can't make a template yourself, open an issue and briefly explain:

- Why should we add and maintain this package?
- Which distro(s) should it be available for?
- Should it be compiled from source or repackage a binary?
- Does it appear to be safe? (no obvious malware, suspicious blobs, etc)

If a package is no longer maintained, or you no longer wish to maintain one (😢), let us know in an issue/PR.

## Pull Requests

The [PR build workflow](https://github.com/UniversalRepository/packages/blob/master/.github/workflows/pr.yml) tests changed packages for Void, Arch, and Chimera. Changes to shared build tooling can cause all packages for the affected distros to be selected.

The workflow uses the `pr-build` environment, so builds may need maintainer approval before starting. PR builds use temporary signing keys and do not publish packages to SourceForge.

You do not need to be a package maintainer to update a given package, but if there are conflicting templates (e.g. person A wishes to make X changes and person B, the maintainer, wishes to make Y changes, the latter will more likely be honored.)

## Commit style

The commit style (`scope: message`) should be kept clear and concise. The scope tells us what changed, and the message tells us what was done.

For packages, use `distro/package`, e.g. `void/noctalia`. For other changes, use the relevant component or path, e.g. `void`, `src/cli`, `ci/pr`, `ci/container`, or `docs/readme`. You do not need to include the file extension or a leading dot from `.ci` or `.github`.

Here are some examples

| Case | Commit message |
|------|----------------|
| Adding a new package | `void/svc: new package at 1.0.0` |
| Updating a package | `void/noctalia: update to 5.4.0` |
| Fixing a package | `chimera/umbriel: fix build dependency` |
| Removing a package | `void/foo: remove package` |
| Orphaning a package | `void/foo: orphaned` |
| Related changes to several packages in one distro | `void/*: rebuild against new library version` |
| Related changes across distros | `*/*: update shared maintainer address` |
| Distro backend changes | `arch: fix repository signing` |
| Shared CLI changes | `src/cli: improve invalid target error` |
| Distro-specific CI changes | `ci/chimera: support new distro` |
| Shared CI changes | `ci: fix package selection` |
| Container changes | `ci/container: add build dependency` |
| Documentation changes | `docs/readme: add chimera instructions` |

Start the description with a lowercase word, but keep proper names and technical capitalization where appropriate. Do not add a trailing period. Try to keep the first line around 72 characters or less, but don't make the message unclear just to fit it.

We do not require `feat:`, `fix:`, `chore:`, etc. Use the affected package or component as the scope instead.

Keep unrelated changes in separate commits. For example, updating two unrelated packages should normally be two commits. If a backend change also requires a dispatcher change to work, those can stay together. Use `void/*` or `*/*` only when the changes are actually related, not just because several files were staged together.

For a simple package update, the first line is usually enough. If the change needs more explanation, leave a blank line and add a body explaining why it is needed, any compatibility impact, and how it was tested. Package removals should include the reason. Details such as new completions, patches, or changed dependencies can go in the body or PR description.

## Backend changes

Contributions to the build system are welcome too. Keep distro-specific behavior in its backend, and shared behavior in `src/`. Use the distro's existing build tools rather than reimplementing them.

The current entry point and backends use Bash. Follow the surrounding code, keep dependencies minimal, and avoid adding abstractions for things we don't use yet.

For fixes, briefly explain the original failure and how your change fixes it. Include the command used to reproduce it and any relevant logs. If changing shared code, test the affected backends, not just the one that first showed the problem.

### Adding a new distro

Open an issue or draft PR describing the distro, its packaging tools, and how you intend to build and publish packages. You don't need to have everything finished before asking for help.

A new backend needs more than a script that produces a package. It also needs to select packages for rebuilding, sign and index the output, and work with the existing CI workflow. These are the main parts to look at:

| Part | What to add or change |
|------|-----------------------|
| `DISTRO/build.sh` | Define `distro_build()` and handle environment preparation, building, indexing, and signing |
| Package directory | Keep recipes and supporting files under the distro's directory, following its normal packaging layout |
| `.ci/backends/DISTRO.sh` | Read expected package metadata and compare it with packages already built |
| `Containerfile` | Add the necessary tools and checks that they are available |
| `.github/workflows/build.yml` | Add the distro to the existing matrix and configure output paths, signing keys, and repository metadata patterns |
| `.github/workflows/pr.yml` | Add PR package selection, build settings, and temporary signing key generation |
| `.ci/index.py` | Add support for reading the distro's repository metadata into `packages.json` where needed |
| `README.md` | Document supported targets, local requirements, signing, and installation |

The dispatcher in `src/distro.sh` loads `DISTRO/build.sh` based on the target name. `distro_build()` receives full targets such as `DISTRO/foo`, grouped by distro. Keep the public interface as `./urepo build DISTRO/PACKAGE`; don't add a separate command for each distro. The existing backends are examples of how this fits together.

The CI selection adapter must define `ci_config()`, `ci_prepare()`, `ci_expected()`, and `ci_available()`. `ci_config()` sets `ARCH`, `PKGS_DIR`, `REPO_DIR`, and `TEMPLATE`. Both metadata hooks output one `name version architecture` record per package, including subpackages. Keep diagnostics on stderr. If the distro uses a different recipe layout, override `ci_recipes()` and `ci_has_recipe()` as needed.

Use the distro's metadata tools where possible. The selector must notice missing subpackages and changed revisions/releases, and skip unsupported architectures. Avoid changing the shared selector just to accommodate behavior that belongs in an adapter.

Keep the existing matrix-based workflow rather than creating a separate workflow for every distro. Check the distro-specific cases too: adding a matrix entry alone does not add recipe discovery or signing support. CI should prepare the runner and publish results; the backend should remain usable locally without GitHub Actions or SourceForge credentials.

Use test signing keys while developing. Document any new key format or CI secret required, but leave production credentials to the maintainers. PR builds must continue to use temporary keys and must not publish packages.

Before calling the backend "ready," please test:

- A first build with an empty build directory, followed by another build using the existing environment.
- Multiple package targets, including a package with subpackages if supported.
- Selection with no existing output, complete output, a missing subpackage, and an updated version/revision.
- Installing from the generated repository with signature verification enabled.
- Adding a second package without losing the first package from the repository metadata.
- A failed build returning a nonzero status, without publishing incomplete results.
- Other potential edge cases that may not be mentioned here.

Include a small working package and explain any remaining limitations, e.g. native builds only or an unsupported architecture. Support can be added in stages, but unfinished backends should be clearly marked as such.

---

Follow the same spirit as official distro packaging, but don't worry if it doesn't fit perfect. That's why this repo exists
