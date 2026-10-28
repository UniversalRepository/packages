import importlib.util
import io
import json
import plistlib
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("index.py")
SPEC = importlib.util.spec_from_file_location("index", SCRIPT)
index = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(index)


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "published"
        self.root.mkdir()

    def archive(self, name, files):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(path, "w:gz") as archive:
            for name, value in files.items():
                data = value.encode() if isinstance(value, str) else value
                member = tarfile.TarInfo(name)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
        return path

    def void(self, name="void/x86_64-repodata", **values):
        info = {
            "pkgver": "foo-bar-1.2_3",
            "architecture": "x86_64",
            "short_desc": "Test package",
            "filename-size": 123,
            "installed_size": 0,
            "filename-sha256": "AB" * 32,
            **values,
        }
        return self.archive(name, {"index.plist": plistlib.dumps({"foo-bar": info})})

    def arch(self, name="arch/x86_64/test.db.tar.gz", **values):
        info = {
            "NAME": "foo",
            "VERSION": "2:1.0-3",
            "ARCH": "any",
            "DESC": "Test",
            "FILENAME": "foo-1.0-3-any.pkg.tar.zst",
            "LICENSE": "MIT\nBSD",
            "CSIZE": "123",
            "ISIZE": "456",
            **values,
        }
        text = "\n\n".join(f"%{key}%\n{value}" for key, value in info.items()) + "\n\n"
        return self.archive(name, {"foo-1.0-3/desc": text})

    def test_formats_and_unknown_distro(self):
        self.void("another-distro/nonfree/x86_64-repodata")
        self.arch()
        self.archive(
            "alpine/user/debug/x86_64/APKINDEX.tar.gz",
            {
                "APKINDEX": "P:foo-dbg\nV:1.0-r0\nA:x86_64\nS:45\nI:90\nC:Q1not-a-file-sha256\n\n"
            },
        )
        result = index.generate(self.root)
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(len(result["packages"]), 3)
        apk, void, arch = result["packages"]
        self.assertEqual(apk["repository"], "user/debug")
        self.assertIsNone(apk["sha256"])
        self.assertEqual(void["distro"], "another-distro")
        self.assertEqual(void["repository"], "nonfree")
        self.assertEqual(void["version"], "1.2_3")
        self.assertEqual(void["sha256"], "ab" * 32)
        self.assertEqual(void["installed_size"], 0)
        self.assertEqual(arch["version"], "2:1.0-3")
        self.assertIsNone(arch["repository"])
        self.assertEqual(arch["architecture"], "any")
        self.assertEqual(arch["license"], "MIT BSD")
        self.assertEqual(arch["download_size"], 123)
        self.assertEqual(arch["path"], "arch/x86_64/foo-1.0-3-any.pkg.tar.zst")
        self.assertEqual(index.generate(self.root)["packages"], result["packages"])

    def test_aliases_and_signatures(self):
        path = self.arch()
        shutil.copyfile(path, path.with_name("test.db"))
        path.with_name(path.name + ".sig").write_text("signature")
        self.assertEqual(len(index.generate(self.root)["packages"]), 1)

    def test_apk_v3_and_compatibility_alias(self):
        from unittest.mock import patch

        path = self.root / "chimera/user/x86_64/Packages.adb"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"ADBd")
        path.with_name("APKINDEX.tar.gz").write_bytes(b"ADBd")
        metadata = {
            "packages": [
                {
                    "name": "foo",
                    "version": "1-r0",
                    "arch": "x86_64",
                    "hashes": "ab" * 20,
                }
            ]
        }
        with patch.object(
            index.subprocess,
            "run",
            return_value=subprocess.CompletedProcess([], 0, json.dumps(metadata)),
        ) as run:
            packages = index.generate(self.root)["packages"]
        self.assertEqual(run.call_count, 1)
        self.assertEqual(packages[0]["path"], "chimera/user/x86_64/foo-1-r0.apk")
        self.assertIsNone(packages[0]["sha256"])

    @unittest.skipUnless(shutil.which("zstd"), "zstd is unavailable")
    def test_zstd_repodata(self):
        path = self.void()
        raw = path.with_name("raw.tar")
        with tarfile.open(path) as source, tarfile.open(raw, "w") as dest:
            for member in source:
                dest.addfile(member, source.extractfile(member))
        path.write_bytes(
            subprocess.run(
                ["zstd", "-c", str(raw)], check=True, capture_output=True
            ).stdout
        )
        self.assertEqual(index.generate(self.root)["packages"][0]["name"], "foo-bar")

    def test_invalid_metadata(self):
        for values in (
            {"architecture": ""},
            {"filename-size": -1},
            {"filename-sha256": "abcd"},
        ):
            with self.subTest(values=values):
                self.void(**values)
                with self.assertRaises(ValueError):
                    index.generate(self.root)

    def test_path_traversal(self):
        self.arch(FILENAME="../outside.pkg.tar.zst")
        with self.assertRaises(ValueError):
            index.generate(self.root)

    def test_absent_metadata(self):
        with self.assertRaisesRegex(ValueError, "no repository metadata"):
            index.generate(self.root)

    def test_atomic_output_and_failure(self):
        self.void()
        output = Path(self.temp.name) / "packages.json"
        command = [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(self.root),
            "--output",
            str(output),
        ]
        subprocess.run(command, check=True, capture_output=True)
        original = output.read_bytes()
        self.assertEqual(json.loads(original)["packages"][0]["name"], "foo-bar")
        self.arch().write_bytes(b"broken database")
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("error:", result.stderr)
        self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
