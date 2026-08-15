from pathlib import Path
import base64, hashlib, sys, zipfile

root = Path(__file__).resolve().parents[1]


def fail(msg):
    print("HX_RELEASE_VERIFY_FAIL:", msg, file=sys.stderr)
    raise SystemExit(1)


pkg = (root / "hxempirical.pkg").read_text(encoding="utf-8").splitlines()
managed = [x.split(None, 1)[1].strip() for x in pkg if x.startswith("f ")]
versions = [x.split(None, 2)[2].strip() for x in pkg if x.startswith("d Version ")]
if len(versions) != 1:
    fail("package version missing/duplicated")
version = versions[0]

for rel in managed:
    if not (root / rel).is_file():
        fail("managed file missing: " + rel)

checks = {
    "README.md": f"当前发布版本：{version}",
    "hxempirical.ado": f'"{version}"',
    "hxempirical.sthlp": f"version {version}",
    "src/main/java/com/hexie/stata/HxWorkbench.java": f'VERSION = "{version}"',
}
for rel, needle in checks.items():
    if needle not in (root / rel).read_text(encoding="utf-8"):
        fail("version mismatch: " + rel)

with zipfile.ZipFile(root / "hxworkbench.jar") as jar:
    class_names = [n for n in jar.namelist() if n.endswith(".class")]
    if not class_names:
        fail("shipped JAR contains no class files")
    class_bytes = b"".join(jar.read(n) for n in class_names)
    if version.encode("utf-8") not in class_bytes:
        fail("shipped JAR version mismatch")

meta = {}
parts = []
for line in (root / "hxempirical-release.index").read_text(encoding="utf-8").splitlines():
    if line.startswith("d "):
        _, key, value = line.split(None, 2)
        meta[key] = value.strip()
    elif line.startswith("f "):
        parts.append(line.split(None, 1)[1].strip())
if not {"archive", "bytes", "sha256", "parts"} <= set(meta):
    fail("release index metadata incomplete")
if int(meta["parts"]) != len(parts):
    fail("part count mismatch")

raw = (root / meta["archive"]).read_bytes()
if len(raw) != int(meta["bytes"]):
    fail("zip byte count mismatch")
if hashlib.sha256(raw).hexdigest() != meta["sha256"].lower():
    fail("zip sha256 mismatch")

b64 = "".join("".join((root / p).read_text(encoding="utf-8").split()) for p in parts)
if base64.b64decode(b64, validate=True) != raw:
    fail("base64 parts mismatch")

expected = set(managed) | {"hxempirical.pkg", "hxinstall.do", "hxinstall_offline.do", "INSTALL.md"}
with zipfile.ZipFile(root / meta["archive"]) as release:
    names = set(release.namelist())
    if names != expected:
        fail(f"zip manifest mismatch missing={sorted(expected - names)} extra={sorted(names - expected)}")
    for rel in sorted(expected):
        packaged = release.read(rel)
        working = (root / rel).read_bytes()
        if packaged != working:
            fail("zip content mismatch: " + rel)

print(
    f"HX_RELEASE_VERIFY_OK version={version} managed={len(managed)} "
    f"zip_files={len(expected)} parts={len(parts)} sha256={meta['sha256']} content_match=1"
)
