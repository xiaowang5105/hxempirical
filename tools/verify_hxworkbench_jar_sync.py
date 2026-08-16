from __future__ import annotations

import hashlib
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.java"
MARKER = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.jar-source"
JAR = ROOT / "hxworkbench.jar"


def fail(message: str) -> None:
    print(f"HX_JAR_SYNC_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def expected_source_sha() -> str:
    if not MARKER.is_file():
        fail(f"missing JAR provenance marker: {MARKER.relative_to(ROOT)}")
    values = [
        line.strip()
        for line in MARKER.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(values) != 1 or len(values[0]) != 40 or any(c not in "0123456789abcdef" for c in values[0].lower()):
        fail("JAR provenance marker must contain exactly one 40-character Git blob SHA-1")
    return values[0].lower()


def verify_jar() -> set[int]:
    if not JAR.is_file():
        fail("hxworkbench.jar is missing")
    majors: set[int] = set()
    with zipfile.ZipFile(JAR) as archive:
        names = archive.namelist()
        classes = [name for name in names if name.endswith(".class")]
        if not classes:
            fail("hxworkbench.jar contains no class files")
        if any(name.startswith("com/stata/sfi/") for name in names):
            fail("hxworkbench.jar must not bundle Stata SFI classes")
        if not any(name == "com/hexie/stata/HxWorkbench.class" for name in names):
            fail("HxWorkbench.class is missing from hxworkbench.jar")
        for name in classes:
            header = archive.read(name)[:8]
            if len(header) != 8:
                fail(f"truncated class file: {name}")
            magic, _minor, major = struct.unpack(">IHH", header)
            if magic != 0xCAFEBABE:
                fail(f"invalid class header: {name}")
            majors.add(major)
    if not majors or max(majors) > 55:
        fail(f"Java class level must be Java 11 or older; found {sorted(majors)}")
    return majors


def main() -> None:
    expected = expected_source_sha()
    actual = git_blob_sha1(SOURCE)
    if actual != expected:
        fail(
            "shipped hxworkbench.jar is stale relative to HxWorkbench.java "
            f"(jar source={expected}, current source={actual}). "
            "Rebuild with tools/build_hxworkbench_jar.ps1 using Stata's real sfi-api.jar."
        )
    majors = verify_jar()
    print(f"HX_JAR_SYNC_OK source={actual} java_major={','.join(map(str, sorted(majors)))}")


if __name__ == "__main__":
    main()
