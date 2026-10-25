import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def apk(*args):
    return subprocess.run(
        [os.environ.get("CBUILD_APK_PATH", "apk"), *map(str, args)],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "APK_CONFIG": "/dev/null"},
    ).stdout


def record(info, category=None):
    fields = [info[name] for name in ("name", "version", "arch")]
    if any(
        not isinstance(value, str) or not value or len(value.split()) != 1
        for value in fields
    ):
        raise ValueError("invalid APK metadata record")
    if category:
        fields[0] = f"{category}/{fields[0]}"
    return tuple(fields)


def read_apk(path):
    return json.loads(apk("adbdump", "--format", "json", path))


def expected_records(recipe, arch):
    metadata = json.load(sys.stdin)
    if len(metadata) != 1:
        raise ValueError(f"expected one cbuild template: {recipe}")
    pkg = metadata[0]
    if pkg["broken"] == f"this package cannot be built for {arch}":
        return []
    if pkg["broken"]:
        raise ValueError(f"{recipe}: {pkg['broken']}")
    if pkg["restricted"]:
        raise ValueError(f"{recipe}: restricted packages are not enabled")
    category = recipe.split("/", 1)[0]
    version = f"{pkg['pkgver']}-r{pkg['pkgrel']}"
    return [
        record({"name": name, "version": version, "arch": arch}, category)
        for name in [pkg["pkgname"], *pkg["subpackages"]]
    ]


def check_built(recipe, arch, repo):
    records = expected_records(recipe, arch)
    if not records:
        raise ValueError(f"{recipe}: unsupported architecture {arch}")
    category = recipe.split("/", 1)[0]
    for identity in records:
        name, version, _ = identity
        path = Path(repo) / category / arch / f"{name.split('/', 1)[1]}-{version}.apk"
        if record(read_apk(path)["info"], category) != identity:
            raise ValueError(f"unexpected package metadata: {path}")


def available(repo, arch):
    for category in ("main", "user"):
        for path in sorted((Path(repo) / category / arch).glob("*.apk")):
            apk("verify", "--allow-untrusted", path)
            print(*record(read_apk(path)["info"], category))


def verify(repo, keys):
    repo = Path(repo)
    index = repo / "Packages.adb"
    archives = sorted(repo.glob("*.apk"))
    if not archives:
        if index.exists():
            raise ValueError(f"index without packages: {index}")
        return
    apk("verify", "--keys-dir", keys, index)
    indexed = {}
    for info in read_apk(index)["packages"]:
        identity = record(info)
        if identity[0] in indexed:
            raise ValueError(f"duplicate package in index: {identity[0]}")
        indexed[identity[0]] = info
    actual = {}
    for path in archives:
        apk("verify", "--keys-dir", keys, path)
        info = read_apk(path)["info"]
        actual[record(info)] = path
    identities = {record(info) for info in indexed.values()}
    if {item[0] for item in actual} != set(indexed) or not identities <= actual.keys():
        raise ValueError(f"package/index mismatch: {repo}")
    with tempfile.TemporaryDirectory(prefix="urepo-chimera-index-") as temp:
        check_index = Path(temp) / "Packages.adb"
        apk(
            "mkndx",
            "--keys-dir",
            keys,
            "--hash",
            "sha256-160",
            "--output",
            check_index,
            *[actual[item] for item in sorted(identities)],
        )
        generated = {record(info): info for info in read_apk(check_index)["packages"]}
    for identity in identities:
        old, new = indexed[identity[0]], generated[identity]
        if any(old.get(field) != new.get(field) for field in ("hashes", "file-size")):
            raise ValueError(
                f"stale package hash in index: {repo / actual[identity].name}"
            )
    compatibility = repo / "APKINDEX.tar.gz"
    if not compatibility.is_file() or compatibility.read_bytes() != index.read_bytes():
        raise ValueError(f"missing or stale compatibility index: {compatibility}")


def main():
    match sys.argv[1:]:
        case ["expected", recipe, arch]:
            for item in expected_records(recipe, arch):
                print(*item)
        case ["check-built", recipe, arch, repo]:
            check_built(recipe, arch, repo)
        case ["available", repo, arch]:
            available(repo, arch)
        case ["verify", repo, keys]:
            verify(repo, keys)
        case _:
            raise ValueError(
                "usage: metadata.py expected RECIPE ARCH | check-built RECIPE ARCH REPO | available REPO ARCH | verify REPO KEYS"
            )


if __name__ == "__main__":
    try:
        main()
    except (
        ValueError,
        KeyError,
        TypeError,
        OSError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            print(exc.stderr, file=sys.stderr, end="")
        sys.exit(1)
