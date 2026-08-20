from pathlib import Path
import base64
import hashlib
import re
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
PORTABLE_TEXT_SUFFIXES = {".ado", ".do", ".sthlp", ".dlg", ".md", ".pkg", ".toc"}


def fail(msg):
    print("HX_RELEASE_VERIFY_FAIL:", msg, file=sys.stderr)
    raise SystemExit(1)


def read_text(path):
    return (root / path).read_text(encoding="utf-8")


def portable_bytes(path):
    path = Path(path)
    raw = (root / path).read_bytes()
    if path.suffix.lower() in PORTABLE_TEXT_SUFFIXES:
        text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        return text.encode("utf-8")
    return raw


def posix_checksum(data):
    polynomial = 0x04C11DB7
    table = []
    for index in range(256):
        value = index << 24
        for _ in range(8):
            value = ((value << 1) ^ polynomial) & 0xFFFFFFFF if value & 0x80000000 else (value << 1) & 0xFFFFFFFF
        table.append(value)
    crc = 0
    for byte in data:
        crc = ((crc << 8) & 0xFFFFFFFF) ^ table[((crc >> 24) ^ byte) & 0xFF]
    length = len(data)
    while length:
        byte = length & 0xFF
        crc = ((crc << 8) & 0xFFFFFFFF) ^ table[((crc >> 24) ^ byte) & 0xFF]
        length >>= 8
    return (~crc) & 0xFFFFFFFF


pkg = read_text("hxempirical.pkg").splitlines()
managed = [x.split(None, 1)[1].strip() for x in pkg if len(x) > 2 and x[0].lower() == "f" and x[1].isspace()]
versions = [x.split(None, 2)[2].strip() for x in pkg if x.startswith("d Version ")]
if len(versions) != 1:
    fail("package version missing/duplicated")
version = versions[0]

for rel in managed:
    if not (root / rel).is_file():
        fail("managed file missing: " + rel)

# All public/current version surfaces must agree with hxempirical.pkg.
checks = {
    "README.md": f"当前发布版本：{version}",
    "INSTALL.md": (f"当前版本：{version}", f"最新版本：{version}"),
    "hxempirical.ado": (f"hxempirical {version}", f'"{version}"'),
    "hxempirical.sthlp": f"version {version}",
    "hxinstall.do": f"hxinstall {version}",
    "hxinstaller.ado": f"hxinstaller {version}",
    "src/main/java/com/hexie/stata/HxWorkbench.java": f'VERSION = "{version}"',
}
for rel, needles in checks.items():
    text = read_text(rel)
    if isinstance(needles, str):
        needles = (needles,)
    for needle in needles:
        if needle not in text:
            fail(f"version mismatch: {rel} missing {needle!r}")

# The shipped JAR must contain classes and expose the current public version.
with zipfile.ZipFile(root / "hxworkbench.jar") as jar:
    jar_names = jar.namelist()
    class_names = [n for n in jar_names if n.endswith(".class")]
    if not class_names:
        fail("shipped JAR contains no class files")
    if len(jar_names) != len(set(jar_names)):
        fail("shipped JAR contains duplicate entries")
    class_bytes = b"".join(jar.read(n) for n in class_names)
    if version.encode("utf-8") not in class_bytes:
        fail("shipped JAR version mismatch")

# Parse and validate the text-release index.
meta = {}
parts = []
for line in read_text("hxempirical-release.index").splitlines():
    if line.startswith("d "):
        _, key, value = line.split(None, 2)
        if key in meta:
            fail("duplicate release-index metadata key: " + key)
        meta[key] = value.strip()
    elif line.startswith("f "):
        parts.append(line.split(None, 1)[1].strip())
required_meta = {
    "archive", "package", "version", "pkg_bytes", "pkg_checksum",
    "pkg_sha256", "bytes", "checksum", "sha256", "parts", "offline_index",
}
if not required_meta <= set(meta):
    fail("release index metadata incomplete")
if meta["archive"] != "hxempirical-release.zip":
    fail("unexpected release archive name: " + meta["archive"])
try:
    indexed_part_count = int(meta["parts"])
    indexed_bytes = int(meta["bytes"])
except ValueError:
    fail("release index bytes/parts must be integers")
if indexed_part_count != len(parts):
    fail("part count mismatch")
expected_parts = [f"release/hxempirical-release.b64.{i:03d}" for i in range(1, indexed_part_count + 1)]
if parts != expected_parts:
    fail("release parts must be contiguous and ordered from 001")
if len(parts) != len(set(parts)):
    fail("release index contains duplicate part paths")
if not re.fullmatch(r"[0-9a-fA-F]{64}", meta["sha256"]):
    fail("release index sha256 is not a 64-digit hexadecimal digest")

raw = (root / meta["archive"]).read_bytes()
if len(raw) != indexed_bytes:
    fail("zip byte count mismatch")
if hashlib.sha256(raw).hexdigest() != meta["sha256"].lower():
    fail("zip sha256 mismatch")
if posix_checksum(raw) != int(meta["checksum"]):
    fail("zip POSIX checksum mismatch")

package = portable_bytes("hxempirical.pkg")
if meta["package"] != "hxempirical.pkg" or meta["version"] != version:
    fail("release index package/version binding mismatch")
if len(package) != int(meta["pkg_bytes"]):
    fail("package byte count mismatch")
if posix_checksum(package) != int(meta["pkg_checksum"]):
    fail("package POSIX checksum mismatch")
if hashlib.sha256(package).hexdigest() != meta["pkg_sha256"].lower():
    fail("package sha256 mismatch")

b64 = "".join("".join((root / p).read_text(encoding="utf-8").split()) for p in parts)
try:
    reconstructed = base64.b64decode(b64, validate=True)
except Exception as exc:
    fail(f"base64 parts are invalid: {exc}")
if reconstructed != raw:
    fail("base64 parts mismatch")

# The release ZIP is the actual installer payload: no missing, extra, duplicate, or stale files.
offline_name = meta.get("offline_index", "")
if offline_name != "hxempirical-offline.index":
    fail("release index does not bind the offline integrity index")
expected = set(managed) | {"hxempirical.pkg", "hxinstall.do", "hxinstall_offline.do", "INSTALL.md", offline_name}
with zipfile.ZipFile(root / meta["archive"]) as release:
    name_list = release.namelist()
    if len(name_list) != len(set(name_list)):
        fail("release ZIP contains duplicate entries")
    names = set(name_list)
    if names != expected:
        fail(f"zip manifest mismatch missing={sorted(expected - names)} extra={sorted(names - expected)}")
    for rel in sorted(expected - {offline_name}):
        packaged = release.read(rel)
        working = portable_bytes(rel)
        if packaged != working:
            fail("zip content mismatch: " + rel)

    offline_lines = release.read(offline_name).decode("utf-8").splitlines()
    offline_files = [line.split()[1] for line in offline_lines if line.startswith("f ")]
    if offline_files != managed:
        fail("offline integrity index does not match the package manifest order")
    offline_meta = {}
    offline_records = {}
    for line in offline_lines:
        fields = line.split()
        if len(fields) >= 3 and fields[0] == "d":
            offline_meta[fields[1]] = " ".join(fields[2:])
        elif len(fields) == 4 and fields[0] == "f":
            offline_records[fields[1]] = (int(fields[2]), int(fields[3]))
    if offline_meta.get("package") != "hxempirical.pkg" or offline_meta.get("version") != version:
        fail("offline integrity package/version binding mismatch")
    if int(offline_meta.get("pkg_bytes", -1)) != len(package) or int(offline_meta.get("pkg_checksum", -1)) != posix_checksum(package):
        fail("offline integrity package checksum mismatch")
    for rel in managed:
        working = portable_bytes(rel)
        if offline_records.get(rel) != (len(working), posix_checksum(working)):
            fail("offline integrity file checksum mismatch: " + rel)

print(
    f"HX_RELEASE_VERIFY_OK version={version} managed={len(managed)} "
    f"zip_files={len(expected)} parts={len(parts)} sha256={meta['sha256']} "
    "content_match=1 version_surfaces=1 ordered_parts=1 duplicate_entries=0"
)
