from pathlib import Path
import hashlib
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def fail(message):
    print("HX_DIRECT_IMPORT_VERIFY_FAIL:", message, file=sys.stderr)
    raise SystemExit(1)

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

helper = read("src/main/java/com/hexie/stata/HxDirectImportHook.java")
launcher = read("hxtoolbox.ado")
workbench = read("src/main/java/com/hexie/stata/HxWorkbench.java")
for needle in (
    "Excel / CSV 转换为 DTA",
    "导入 Excel/CSV",
    "导入 Excel / CSV",
    "convertLoadAfter",
    "convertProtectLeadingZeros",
    "convertDelimitedFirstRow",
    "runConvertDta",
    "detectExternalFile",
    "sample.xlsx",
    "sample.xls",
    "sample.csv",
    "企业数据.dta",
):
    if needle not in helper:
        fail(f"direct-import hook contract missing: {needle}")
if "import com.stata.sfi" in helper:
    fail("direct-import hook must compile without fake or bundled Stata SFI classes")
if "HxDirectImportHook install" not in launcher:
    fail("hxtoolbox does not install the direct-import hook after launch")
for needle in ("convertInputFile", "convertOutputFile", "convertLoadAfter", "runConvertDta", "detectExternalFile"):
    if needle not in workbench:
        fail(f"existing conversion engine surface missing: {needle}")
with zipfile.ZipFile(ROOT / "hxworkbench.jar") as jar:
    names = jar.namelist()
    if "com/hexie/stata/HxDirectImportHook.class" not in names:
        fail("production JAR does not contain HxDirectImportHook.class")
    if any(name.startswith("com/stata/sfi/") for name in names):
        fail("production JAR bundles Stata SFI classes")
print("HX_DIRECT_IMPORT_VERIFY_OK formats=xlsx,xls,csv output=dta load_after=1 existing_engine=1 sfi_bundled=0")
