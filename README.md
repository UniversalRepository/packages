<div align="center">

# UniversalRepository Packages

[![Packages](https://img.shields.io/github/actions/workflow/status/UniversalRepository/packages/build.yml?branch=master&label=workflow&logo=github&style=plastic)](https://github.com/UniversalRepository/packages/actions/workflows/build.yml)
[![GHCR](https://img.shields.io/badge/GHCR-builder-2496ED?style=plastic&logo=github&logoColor=white)](https://github.com/UniversalRepository/packages/pkgs/container/builder)
[![License](https://img.shields.io/github/license/UniversalRepository/packages?style=plastic)](LICENSE)

This repository serves as the central package collection for UniversalRepository,
housing build definitions, package templates, and source patches across multiple
Linux distributions.

</div>

## Distributions

Currently only x86_64 targets are supported.

| Distro | Path | Format | Build System | Status |
| ------ | ---- | ------ | ------------ | ------ |
| Arch Linux | `arch/pkgs` | `PKGBUILD` | `makepkg` | Supported |
| Void Linux (glibc) | `void/srcpkgs` | `template` | `xbps-src` | Supported |
| Chimera Linux | `chimera/main`, `chimera/user` | `template.py` | `cbuild` | Supported |
| Fedora / openSUSE | `rpm/specs` | `SPEC` | `rpmbuild` | In Progress |

## Installation

Binary packages for each supported distro are published over on [SourceForge](https://sourceforge.net/projects/universalrepository).

<details>
<summary><strong>Arch Linux</strong></summary>

### 1. Add the repository
Add the following to the end of `/etc/pacman.conf`:
```ini
[universalrepository]
SigLevel = Required TrustedOnly
Server = https://sourceforge.net/projects/universalrepository/files/arch/
```

### 2. Import the key and sync
Download and import our public key:
```bash
curl -fLo universalrepository.asc https://downloads.sourceforge.net/project/universalrepository/arch/universalrepository.asc
sudo pacman-key --add universalrepository.asc
```

Check its fingerprint:
```bash
sudo pacman-key --finger C57FBE5A22ED5000C8149B21A7CA149CF8A6B28C
```

It should match: `C57F BE5A 22ED 5000 C814 9B21 A7CA 149C F8A6 B28C`

If it matches, locally sign the key to trust it:
```bash
sudo pacman-key --lsign-key C57FBE5A22ED5000C8149B21A7CA149CF8A6B28C
rm universalrepository.asc
```

Sync the repositories and update your system:
```bash
sudo pacman -Syu
```

### 3. Packages
Now you can install a package from URepo:
```bash
sudo pacman -S universalrepository/limine-entry-tool
```

List all packages:
```bash
pacman -Sl universalrepository
```
</details>

<details>
<summary><strong>Void Linux</strong></summary>

### 1. Add the repository
```bash
echo 'repository=https://sourceforge.net/projects/universalrepository/files/void' | sudo tee /etc/xbps.d/10-universalrepository.conf
```
### 2. Sync and import the key
```bash
sudo xbps-install -S
```
XBPS will prompt you to import our public key, confirm it: `0f:fa:c3:8e:fd:cd:c9:52:88:f0:34:ca:df:6c:c6:fa`
### 3. Packages
Now you can install a package from URepo:
```bash
sudo xbps-install svc
```
List all packages:
```bash
xbps-query -iM --repository=https://sourceforge.net/projects/univ
ersalrepository/files/void -s ''
```
</details>

<details>
<summary><strong>Chimera Linux</strong></summary>

### 1. Add the repository
This adds the `user` repository:
```bash
echo 'v3 https://downloads.sourceforge.net/project/universalrepository/chimera/user' | sudo tee /etc/apk/repositories.d/00-universalrepository.list
```

If using packages from `main`, add its URL to the same file once that repository contains packages:
```text
v3 https://downloads.sourceforge.net/project/universalrepository/chimera/main
```

### 2. Import the key and sync

Download and install our public key:
```bash
curl -fLo universalrepository.rsa.pub https://downloads.sourceforge.net/project/universalrepository/chimera/universalrepository.rsa.pub
sudo install -m 644 universalrepository.rsa.pub /etc/apk/keys/
rm universalrepository.rsa.pub
```

Sync the repositories:
```bash
sudo apk update
```

### 3. Packages

Now you can install a package from URepo:
```bash
sudo apk add umbriel
```

List packages in the `user` repository:
```bash
apk list --from none --repository https://downloads.sourceforge.net/project/universalrepository/chimera/user
```

For debug symbols, also add the following to the repository file and sync again:
```text
v3 https://downloads.sourceforge.net/project/universalrepository/chimera/user/debug
```

Then install the corresponding debug package:
```bash
sudo apk add umbriel-dbg
```

</details>

## Building packages natively
Building is done simply using the `urepo` entry point:
```bash
./urepo build distro/package
```
This assumes your host system's `$PATH` contains the necessary binaries and tooling, regardless of the chosen target.

## Building in a container
It might be more desirable to build packages in a container, to avoid cluttering the host system. The following commands assume rootless Podman, but can be easily adapted for Docker.
### 1. Build the container image
If using Docker, first make sure to run:
```bash
cp .containerignore .dockerignore
```
Then build:
```bash
podman build --file Containerfile --build-arg "BUILDER_UID=$(id -u)" --build-arg "BUILDER_GID=$(id -g)" --tag localhost/urepo-builder:local .
```
This may take a while, future rebuilds reuse cached layers.
### 2. Prepare signing keys

Builds sign their output. Create/use a key for each distro.

| Distribution | Signing key | Key format |
| --- | --- | --- |
| Void | `keys/void.pem` | RSA private key in PEM format |
| Arch | `keys/arch.key` | OpenPGP private key export, ASCII armored or binary |

### 3. Build packages
Start the container:
```bash
podman run --rm -it --privileged \
    --userns=keep-id --user builder \
    --volume "$PWD:/workspace" \
    localhost/urepo-builder:local
```

If intending to build for Void Linux, use:
```bash
podman run --rm -it --privileged \
    --userns=keep-id --user builder \
    --volume "$PWD:/workspace" \
    --env UREPO_VOID_SIGNED_BY=UniversalRepository \
    --env UREPO_VOID_CHROOT_CMD=bwrap \
    localhost/urepo-builder:local
```

Inside the container image, specify a distro and package to build:
```bash
./urepo build void/svc
```
Multiple targets from different distros can be built together:
```bash
./urepo build void/foo arch/bar
```
