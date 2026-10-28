import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def apk(*args):
    return subprocess.run(
        ["apk", "--repositories-file", "/dev/null", *map(str, args)],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "APK_CONFIG": "/dev/null"},
    ).stdout


def text_member(path, name):
    with tarfile.open(path, "r:gz", ignore_zeros=True) as archive:
        for member in archive:
            if member.name.removeprefix("./") == name and member.isfile():
                return archive.extractfile(member).read().decode()
    raise ValueError(f"{path}: missing {name}")


def record(name, version, arch):
    values = (name, version, arch)
    if any(
        not value or len(value.split()) != 1 or "/" in value or "\\" in value
        for value in values
    ) or name in (".", ".."):
        raise ValueError(f"invalid APK metadata: {values}")
    return values


def package(path, arch, keys=None):
    if path.is_symlink():
        raise ValueError(f"symlink in Alpine repository: {path}")
    trust = ["--keys-dir", keys] if keys else ["--allow-untrusted"]
    apk("verify", *trust, path)
    info = {}
    for line in text_member(path, ".PKGINFO").splitlines():
        if " = " in line:
            key, value = line.split(" = ", 1)
            info[key] = value
    name, version, package_arch = record(info["pkgname"], info["pkgver"], info["arch"])
    if package_arch not in (arch, "noarch"):
        raise ValueError(f"{path}: unexpected architecture {package_arch}")
    if path.name != f"{name}-{version}.apk":
        raise ValueError(f"{path}: filename does not match package metadata")
    return name, version, arch


def available(repo, arch):
    for category in ("main", "community", "testing"):
        for path in sorted((Path(repo) / category / arch).glob("*.apk")):
            name, version, target = package(path, arch)
            print(f"{category}/{name}", version, target)


def check_built(repo):
    expected = [record(*line.split()) for line in sys.stdin if line.strip()]
    if not expected:
        raise ValueError("no expected Alpine packages")
    for name, version, arch in expected:
        path = Path(repo) / f"{name}-{version}.apk"
        if package(path, arch, Path.home() / ".abuild") != (name, version, arch):
            raise ValueError(f"unexpected package metadata: {path}")


def index_records(path):
    records = {}
    for block in text_member(path, "APKINDEX").strip().split("\n\n"):
        if not block:
            continue
        info = dict(line.split(":", 1) for line in block.splitlines())
        identity = record(info["P"], info["V"], info["A"])
        if identity in records:
            raise ValueError(f"duplicate package in index: {identity}")
        records[identity] = info
    return records


def verify(repo, keys, arch, index):
    repo, index = Path(repo), Path(index)
    archives = sorted(repo.glob("*.apk"))
    if not archives:
        raise ValueError(f"index without packages: {index}")
    apk("verify", "--keys-dir", keys, index)
    actual = {package(path, arch, keys) for path in archives}
    indexed = index_records(index)
    if actual != indexed.keys():
        raise ValueError(f"package/index mismatch: {repo}")
    with tempfile.TemporaryDirectory(prefix="urepo-alpine-index-") as directory:
        generated = Path(directory) / "APKINDEX.tar.gz"
        apk(
            "index",
            "--keys-dir",
            keys,
            "--rewrite-arch",
            arch,
            "--output",
            generated,
            *archives,
        )
        if indexed != index_records(generated):
            raise ValueError(f"stale package metadata or hash in index: {index}")


def main():
    match sys.argv[1:]:
        case ["available", repo, arch]:
            available(repo, arch)
        case ["check-built", repo]:
            check_built(repo)
        case ["verify", repo, keys, arch, index]:
            verify(repo, keys, arch, index)
        case _:
            raise ValueError(
                "usage: metadata.py available REPO ARCH | check-built REPO | verify REPO KEYS ARCH INDEX"
            )


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
            print(exc.stderr, file=sys.stderr, end="")
        sys.exit(1)
