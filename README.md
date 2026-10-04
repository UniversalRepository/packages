# UniversalRepository Packages

This repository serves as the central package collection for UniversalRepository, housing build definitions, package templates, and source patches across multiple Linux distributions.

### Supported Distribution Formats
| Distro | Path | Format | BuildSystem |
| ------ | ---- | ------ | ----------- |
| Void   | void/srcpkgs | template | xbps-src|
| Arch   | arch/srcpkgs | PKGBUILD | makepkg |
| Fedora/OpenSUSE | rpm/srcpkgs | SPEC | rpmbuild |

### Repository structure
```bash
.
├── urepo # main cli
├── src
│   ├── cli.sh
│   └── distro.sh
├── LICENSE
├── README.md
├── arch
│   ├── build.sh
│   └── srcpkgs
├── rpm
│   ├── build.sh
│   └── srcpkgs
└── void
    ├── build.sh
    └── srcpkgs
```