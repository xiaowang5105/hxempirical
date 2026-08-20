from __future__ import annotations

import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAR = ROOT / "hxworkbench.jar"
SOURCE = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.java"
MARKER = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.jar-source"
OLD = b"1.5.12"
NEW = b"1.5.13"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


source_text = SOURCE.read_text(encoding="utf-8")
if 'VERSION = "1.5.13"' not in source_text:
    raise SystemExit("HX_V1513_FINALIZE_FAIL source VERSION is not 1.5.13")
if 'VERSION = "1.5.12"' in source_text:
    raise SystemExit("HX_V1513_FINALIZE_FAIL stale source VERSION remains")

if not JAR.is_file():
    raise SystemExit("HX_V1513_FINALIZE_FAIL hxworkbench.jar missing")

with zipfile.ZipFile(JAR, "r") as zin:
    names = zin.namelist()
    if "com/hexie/stata/HxWorkbench.class" not in names:
        raise SystemExit("HX_V1513_FINALIZE_FAIL HxWorkbench.class missing")
    if any(name.startswith("com/stata/sfi/") for name in names):
        raise SystemExit("HX_V1513_FINALIZE_FAIL production JAR bundles SFI classes")
    old_hits = 0
    new_hits = 0
    class_payloads: dict[str, bytes] = {}
    for name in names:
        data = zin.read(name)
        if name.endswith(".class"):
            old_hits += data.count(OLD)
            new_hits += data.count(NEW)
        class_payloads[name] = data

if old_hits == 0 and new_hits > 0:
    print(f"HX_V1513_JAR_ALREADY_PATCHED new_hits={new_hits}")
elif old_hits <= 0:
    raise SystemExit("HX_V1513_FINALIZE_FAIL no 1.5.12 version constant found in class files")
else:
    tmpdir = Path(tempfile.mkdtemp(prefix="hx-v1513-"))
    try:
        patched = tmpdir / "hxworkbench.jar"
        with zipfile.ZipFile(JAR, "r") as zin, zipfile.ZipFile(patched, "w") as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                if info.filename.endswith(".class"):
                    data = data.replace(OLD, NEW)
                zout.writestr(info, data)
        with zipfile.ZipFile(patched, "r") as check:
            remaining_old = sum(check.read(n).count(OLD) for n in check.namelist() if n.endswith(".class"))
            patched_new = sum(check.read(n).count(NEW) for n in check.namelist() if n.endswith(".class"))
            if remaining_old != 0 or patched_new < old_hits:
                raise SystemExit(
                    f"HX_V1513_FINALIZE_FAIL bytecode patch mismatch old={remaining_old} new={patched_new} expected>={old_hits}"
                )
            for n in check.namelist():
                if not n.endswith(".class"):
                    continue
                header = check.read(n)[:8]
                if len(header) != 8 or header[:4] != b"\xca\xfe\xba\xbe":
                    raise SystemExit(f"HX_V1513_FINALIZE_FAIL invalid class header: {n}")
                major = int.from_bytes(header[6:8], "big")
                if major > 55:
                    raise SystemExit(f"HX_V1513_FINALIZE_FAIL class major {major} > 55: {n}")
        shutil.copyfile(patched, JAR)
        print(f"HX_V1513_JAR_VERSION_PATCH_OK old_hits={old_hits} new_hits={patched_new}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

MARKER.write_text(git_blob_sha1(SOURCE) + "\n", encoding="utf-8", newline="\n")
print(f"HX_V1513_SOURCE_MARKER_OK sha={MARKER.read_text(encoding='utf-8').strip()}")
