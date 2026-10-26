import argparse
import io
import json
import os
import plistlib
import re
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

FIELDS = (
    "name version architecture description homepage license maintainer "
    "download_size installed_size sha256"
).split()


def mapped(info, keys):
    return dict(zip(FIELDS, (info.get(key) for key in keys.split())))


def archive(path):
    with path.open("rb") as source:
        magic = source.read(4)
    if magic == b"\x28\xb5\x2f\xfd":
        data = subprocess.run(
            ["zstd", "-dc", str(path)], check=True, capture_output=True
        ).stdout
        return tarfile.open(fileobj=io.BytesIO(data))
    return tarfile.open(path)


def xbps(path):
    with archive(path) as data:
        packages = plistlib.load(data.extractfile("index.plist"))
    for name, info in packages.items():
        pkgver = info["pkgver"]
        if not pkgver.startswith(name + "-"):
            raise ValueError(f"invalid XBPS pkgver: {pkgver}")
        info = {**info, "name": name, "version": pkgver[len(name) + 1 :]}
        pkg = mapped(
            info,
            "name version architecture short_desc homepage license maintainer "
            "filename-size installed_size filename-sha256",
        )
        yield pkg, f"{pkgver}.{pkg['architecture']}.xbps", path.name[:-9]


def pacman(path):
    with archive(path) as data:
        for member in data:
            if not member.isfile() or PurePosixPath(member.name).name != "desc":
                continue
            info = {}
            for block in data.extractfile(member).read().decode().strip().split("\n\n"):
                key, *values = block.splitlines()
                info[key.strip("%")] = " ".join(values)
            yield (
                mapped(
                    info,
                    "NAME VERSION ARCH DESC URL LICENSE PACKAGER CSIZE ISIZE SHA256SUM",
                ),
                info["FILENAME"],
                path.parent.name,
            )


def apk(path):
    with path.open("rb") as source:
        magic = source.read(3)
    if magic == b"ADB":
        result = subprocess.run(
            [
                os.environ.get("CBUILD_APK_PATH", "apk"),
                "adbdump",
                "--format",
                "json",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "APK_CONFIG": "/dev/null"},
        )
        packages = json.loads(result.stdout)["packages"]
        keys = (
            "name version arch description url license maintainer "
            "file-size installed-size sha256"
        )
    else:
        with archive(path) as data:
            text = data.extractfile("APKINDEX").read().decode()
        packages = [
            dict(line.split(":", 1) for line in block.splitlines())
            for block in text.strip().split("\n\n")
            if block
        ]
        keys = "P V A T U L m S I sha256"
    for info in packages:
        pkg = mapped(info, keys)
        yield pkg, f"{pkg['name']}-{pkg['version']}.apk", path.parent.name


READERS = {
    "*-repodata": xbps,
    "*.db": pacman,
    "*.db.tar.*": pacman,
    "Packages.adb": apk,
    "APKINDEX.tar.gz": apk,
}


def indexes(root):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name.endswith(".sig"):
            continue
        if path.name == "APKINDEX.tar.gz" and path.with_name("Packages.adb").exists():
            continue
        if (
            ".db.tar." in path.name
            and path.with_name(path.name.split(".tar.")[0]).exists()
        ):
            continue
        for pattern, reader in READERS.items():
            if path.match(pattern):
                yield path, reader
                break


def normalize(pkg, filename, target, relative):
    for key in ("name", "version", "architecture"):
        value = pkg[key]
        if not isinstance(value, str) or not value or len(value.split()) != 1:
            raise ValueError(f"invalid {key}: {value!r}")
    for key in ("description", "homepage", "license", "maintainer"):
        value = pkg[key]
        if isinstance(value, list):
            value = " ".join(value)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"invalid {key}: {value!r}")
        pkg[key] = value or None
    for key in ("download_size", "installed_size"):
        value = pkg[key]
        if value is not None:
            if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
                raise ValueError(f"invalid {key}: {value!r}")
            pkg[key] = int(value)
    if pkg["sha256"] is not None:
        if not isinstance(pkg["sha256"], str) or not re.fullmatch(
            r"[0-9a-fA-F]{64}", pkg["sha256"]
        ):
            raise ValueError("invalid SHA-256 checksum")
        pkg["sha256"] = pkg["sha256"].lower()
    if (
        not isinstance(filename, str)
        or not filename
        or filename in (".", "..")
        or "/" in filename
        or "\\" in filename
    ):
        raise ValueError(f"invalid package filename: {filename!r}")
    if len(relative.parts) < 2:
        raise ValueError(f"metadata must be inside a distro directory: {relative}")
    repository = list(relative.parts[1:-1])
    if repository and repository[-1] == target:
        repository.pop()
    return {
        "name": pkg["name"],
        "version": pkg["version"],
        "description": pkg["description"],
        "distro": relative.parts[0],
        "architecture": pkg["architecture"],
        "repository": "/".join(repository) or None,
        **{key: pkg[key] for key in FIELDS[4:]},
        "path": (relative.parent / filename).as_posix(),
    }


def generate(root):
    if not root.is_dir():
        raise ValueError(f"missing repository root: {root}")
    packages = {}
    found = False
    for path, reader in indexes(root):
        found = True
        try:
            for pkg, filename, target in reader(path):
                record = normalize(pkg, filename, target, path.relative_to(root))
                identity = record["path"]
                if identity in packages and packages[identity] != record:
                    raise ValueError(f"conflicting package records: {identity}")
                packages[identity] = record
        except (
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
            tarfile.TarError,
        ) as exc:
            raise ValueError(f"{path}: {exc}") from exc
    if not found:
        raise ValueError("no repository metadata found")
    return {
        "schema_version": 1,
        "updated_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "packages": sorted(
            packages.values(),
            key=lambda pkg: (
                pkg["distro"],
                pkg["repository"] or "",
                pkg["architecture"],
                pkg["name"],
                pkg["version"],
                pkg["path"],
            ),
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Index published repositories by package format"
    )
    parser.add_argument("--root", type=Path, default=Path("published"))
    parser.add_argument("--output", type=Path, default=Path("packages.json"))
    parser.add_argument(
        "--patterns", action="store_true", help="print rsync metadata patterns"
    )
    args = parser.parse_args()
    if args.patterns:
        print("\n".join(READERS))
        return
    result = generate(args.root)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=args.output.parent, delete=False
        ) as file:
            temporary = Path(file.name)
            json.dump(result, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary.chmod(0o644)
        temporary.replace(args.output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f"Indexed {len(result['packages'])} packages into {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        tarfile.TarError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            print(
                exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr,
                file=sys.stderr,
            )
        sys.exit(1)
