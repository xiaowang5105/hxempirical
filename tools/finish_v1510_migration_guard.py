from pathlib import Path

root = Path(__file__).resolve().parents[1]


def read(path):
    return (root / path).read_text(encoding="utf-8")


def write(path, text):
    (root / path).write_text(text, encoding="utf-8", newline="\n")


def once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {n}")
    return text.replace(old, new, 1)

p = "hxinstaller.ado"
s = read(p)
s = once(
    s,
    '''    capture quietly confirm file `"`legacy_root'hxempirical.pkg"'\n    if !_rc local legacy_present 1\n''',
    '''    capture quietly confirm file `"`legacy_root'hxempirical.pkg"'\n    if !_rc local legacy_present 1\n    capture quietly confirm file `"`legacy_root'hxworkbench.jar"'\n    if !_rc local legacy_present 1\n''',
    "legacy jar detection",
)
s = once(
    s,
    '''if `"`action'"' == "update" & `"`installed_version'"' == `"`package_version'"' & `install_complete' {\n''',
    '''if `"`action'"' == "update" & `"`installed_version'"' == `"`package_version'"' & `install_complete' & !`legacy_present' {\n''',
    "fast path must not skip legacy cleanup",
)
write(p, s)

p = "tools/verify_static_contracts.py"
s = read(p)
anchor = '''if "local personal_h" not in read("hxinstaller.ado") or "local target `\\\"`personal_h'\\\"'" not in read("hxinstaller.ado"):\n    fail("transactional installer does not target PERSONAL/h")\n'''
extra = anchor + '''if "& !`legacy_present'" not in read("hxinstaller.ado"):\n    fail("same-version fast path can skip legacy PERSONAL-root cleanup")\nif "legacy_root'hxworkbench.jar" not in read("hxinstaller.ado"):\n    fail("legacy JAR shadow is not detected")\n'''
if anchor not in s:
    raise SystemExit("static layout anchor missing")
s = s.replace(anchor, extra, 1)
write(p, s)
print("HX_V1510_MIGRATION_GUARD_OK")
