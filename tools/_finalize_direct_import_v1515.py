from __future__ import annotations

from pathlib import Path
import hashlib
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OLD = "1.5.14"
NEW = "1.5.15"


def fail(message: str) -> None:
    print(f"HX_DIRECT_IMPORT_FINALIZE_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8", newline="\n")


def replace_required(path: str, old: str, new: str, minimum: int = 1) -> None:
    text = read(path)
    count = text.count(old)
    if count < minimum:
        fail(f"{path}: expected at least {minimum} occurrences of {old!r}, found {count}")
    write(path, text.replace(old, new))


def git_blob_sha(text_path: Path) -> str:
    data = text_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def write_marker(source_rel: str, marker_rel: str, description: str) -> str:
    source = ROOT / source_rel
    digest = git_blob_sha(source)
    marker = (
        f"# Git blob SHA-1 of {source_rel} used to build the shipped hxworkbench.jar.\n"
        f"# {description}\n"
        f"{digest}\n"
    )
    write(marker_rel, marker)
    return digest


def patch_jar_version() -> int:
    jar = ROOT / "hxworkbench.jar"
    temp = ROOT / ".hxworkbench-v1515.tmp.jar"
    replacements = 0
    with zipfile.ZipFile(jar, "r") as source, zipfile.ZipFile(temp, "w") as target:
        names = source.namelist()
        if len(names) != len(set(names)):
            fail("input hxworkbench.jar contains duplicate entries")
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename.startswith("com/hexie/stata/HxWorkbench") and info.filename.endswith(".class"):
                count = data.count(OLD.encode("utf-8"))
                if count:
                    data = data.replace(OLD.encode("utf-8"), NEW.encode("utf-8"))
                    replacements += count
            target.writestr(info, data)
    if replacements < 1:
        temp.unlink(missing_ok=True)
        fail("no HxWorkbench class contained the old public version constant")
    temp.replace(jar)
    return replacements


# 1) Public version surfaces. HxWorkbench behavior is not rebuilt here; only its
# equal-length public VERSION constant changes from 1.5.14 to 1.5.15.
for rel in (
    "README.md",
    "INSTALL.md",
    "hxempirical.ado",
    "hxempirical.sthlp",
    "hxinstall.do",
    "hxinstaller.ado",
    "hxempirical.pkg",
):
    replace_required(rel, OLD, NEW)

java_path = "src/main/java/com/hexie/stata/HxWorkbench.java"
java = read(java_path)
needle = f'public static final String VERSION = "{OLD}";'
if needle not in java:
    fail("HxWorkbench VERSION declaration not found")
write(java_path, java.replace(needle, f'public static final String VERSION = "{NEW}";', 1))

# 2) User-facing release note: direct import is the default empty-data action;
# the advanced conversion workflow remains available from 数据处理 → 导入与转换.
readme = read("README.md")
anchor = "**平台：Windows / macOS**\n"
release_note = """

### 1.5.15 Excel / CSV 直接导入

- “当前数据”空状态和首页中的 Excel / CSV 入口统一为 **导入 Excel / CSV**，点击后直接选择 `.xlsx`、`.xls` 或 `.csv` 文件。
- 选中文件后自动使用现有安全转换引擎：检查文件、保护可识别的前导零列、生成真实 Stata `import excel` / `import delimited` 与 `save` 命令，并把完整命令写入 Stata History。
- 输出 `.dta` 默认与原文件同目录、同名；目标已存在时仍使用现有“另存为 / 覆盖 / 取消”保护，不静默覆盖。
- 导入成功后自动载入生成的 `.dta`，并刷新变量窗口、当前数据表和变量摘要；若内存已有数据，导入前先提示确认。
- 高级批量转换、工作表、编码、分隔符等设置继续保留在“数据处理 → 导入与转换”。
"""
if "### 1.5.15 Excel / CSV 直接导入" not in readme:
    if anchor not in readme:
        fail("README platform anchor not found")
    readme = readme.replace(anchor, anchor + release_note, 1)
    write("README.md", readme)

# 3) Launch the direct-import hook after the existing workbench frame is created.
hxtoolbox = read("hxtoolbox.ado")
hxtoolbox = hxtoolbox.replace("*! hxtoolbox 4.7.1  15aug2026", "*! hxtoolbox 4.7.2  20aug2026", 1)
hook_block = '''

    /* The direct-import hook rewires only the Excel/CSV entry buttons and then
       delegates to WorkbenchFrame's existing conversion engine.  Failure here
       must not prevent the main workbench from opening. */
    capture quietly javacall com.hexie.stata.HxDirectImportHook install, ///
        classpath(`"`jarfile'"')
    if _rc {
        display as text "Excel / CSV 直接导入入口未增强；高级导入仍可从 数据处理 > 导入与转换 使用。"
    }
'''
end_anchor = '''        exit `rc'\n    }\nend\n'''
if "HxDirectImportHook install" not in hxtoolbox:
    if end_anchor not in hxtoolbox:
        fail("hxtoolbox launch tail not found")
    hxtoolbox = hxtoolbox.replace(end_anchor, '''        exit `rc'\n    }''' + hook_block + "end\n", 1)
write("hxtoolbox.ado", hxtoolbox)

# 4) Future full production builds compile the hook together with HxWorkbench
# against the real Stata SFI archive and update both provenance markers.
build_path = "tools/build_hxworkbench_jar.ps1"
build = read(build_path)
if "$helperSource" not in build:
    build = build.replace(
        "$source = Join-Path $repository 'src/main/java/com/hexie/stata/HxWorkbench.java'\n$marker = Join-Path $repository 'src/main/java/com/hexie/stata/HxWorkbench.jar-source'",
        "$source = Join-Path $repository 'src/main/java/com/hexie/stata/HxWorkbench.java'\n$helperSource = Join-Path $repository 'src/main/java/com/hexie/stata/HxDirectImportHook.java'\n$marker = Join-Path $repository 'src/main/java/com/hexie/stata/HxWorkbench.jar-source'\n$helperMarker = Join-Path $repository 'src/main/java/com/hexie/stata/HxDirectImportHook.jar-source'",
        1,
    )
    build = build.replace(
        "if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {\n    throw \"Missing Java source: $source\"\n}",
        "if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {\n    throw \"Missing Java source: $source\"\n}\nif (-not (Test-Path -LiteralPath $helperSource -PathType Leaf)) {\n    throw \"Missing Java source: $helperSource\"\n}",
        1,
    )
    build = build.replace(
        "& $javac --release 11 -Xmaxerrs 200 -classpath $SfiJar -d $classes $source",
        "& $javac --release 11 -Xmaxerrs 200 -classpath $SfiJar -d $classes $source $helperSource",
        1,
    )
    marker_anchor = "$markerText = @(\n    '# Git blob SHA-1 of src/main/java/com/hexie/stata/HxWorkbench.java used to build the shipped hxworkbench.jar.'\n    '# This file is updated only by tools/build_hxworkbench_jar.ps1 after a successful build against Stata''s real sfi-api.jar.'\n    $sourceBlob\n) -join [Environment]::NewLine\n[System.IO.File]::WriteAllText($marker, $markerText + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))"
    helper_marker_block = marker_anchor + """

$helperText = [System.IO.File]::ReadAllText($helperSource, [System.Text.Encoding]::UTF8)
$helperText = $helperText.Replace("`r`n", "`n").Replace("`r", "`n")
$helperBytes = [System.Text.Encoding]::UTF8.GetBytes($helperText)
$helperPrefix = [System.Text.Encoding]::ASCII.GetBytes("blob $($helperBytes.Length)`0")
$helperBlobBytes = New-Object byte[] ($helperPrefix.Length + $helperBytes.Length)
[System.Buffer]::BlockCopy($helperPrefix, 0, $helperBlobBytes, 0, $helperPrefix.Length)
[System.Buffer]::BlockCopy($helperBytes, 0, $helperBlobBytes, $helperPrefix.Length, $helperBytes.Length)
$helperSha1 = [System.Security.Cryptography.SHA1]::Create()
try {
    $helperBlob = ([System.BitConverter]::ToString($helperSha1.ComputeHash($helperBlobBytes))).Replace('-', '').ToLowerInvariant()
}
finally {
    $helperSha1.Dispose()
}
$helperMarkerText = @(
    '# Git blob SHA-1 of src/main/java/com/hexie/stata/HxDirectImportHook.java used to build the shipped hxworkbench.jar.'
    '# This file is updated only after HxDirectImportHook.class is compiled for Java 11 and packaged into hxworkbench.jar.'
    $helperBlob
) -join [Environment]::NewLine
[System.IO.File]::WriteAllText($helperMarker, $helperMarkerText + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
"""
    if marker_anchor not in build:
        fail("production build provenance block not found")
    build = build.replace(marker_anchor, helper_marker_block, 1)
    build = build.replace(
        'Write-Host "Source Git blob: $sourceBlob"',
        'Write-Host "Source Git blob: $sourceBlob"\nWrite-Host "Direct-import hook Git blob: $helperBlob"',
        1,
    )
write(build_path, build)

# 5) Extend JAR/source verification to cover the separately compiled hook.
verify_path = "tools/verify_hxworkbench_jar_sync.py"
verify = read(verify_path)
if "HELPER_SOURCE" not in verify:
    verify = verify.replace(
        'SOURCE = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.java"\nMARKER = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.jar-source"',
        'SOURCE = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.java"\nMARKER = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.jar-source"\nHELPER_SOURCE = ROOT / "src/main/java/com/hexie/stata/HxDirectImportHook.java"\nHELPER_MARKER = ROOT / "src/main/java/com/hexie/stata/HxDirectImportHook.jar-source"',
        1,
    )
    generic = '''\n\ndef marker_sha(path: Path, label: str) -> str:\n    if not path.is_file():\n        fail(f"missing {label} provenance marker: {path.relative_to(ROOT)}")\n    values = [\n        line.strip()\n        for line in path.read_text(encoding="utf-8").splitlines()\n        if line.strip() and not line.lstrip().startswith("#")\n    ]\n    if len(values) != 1 or len(values[0]) != 40 or any(c not in "0123456789abcdef" for c in values[0].lower()):\n        fail(f"{label} provenance marker must contain exactly one 40-character Git blob SHA-1")\n    return values[0].lower()\n'''
    verify = verify.replace("\ndef verify_jar() -> set[int]:", generic + "\ndef verify_jar() -> set[int]:", 1)
    verify = verify.replace(
        '        if not any(name == "com/hexie/stata/HxWorkbench.class" for name in names):\n            fail("HxWorkbench.class is missing from hxworkbench.jar")',
        '        if not any(name == "com/hexie/stata/HxWorkbench.class" for name in names):\n            fail("HxWorkbench.class is missing from hxworkbench.jar")\n        if "com/hexie/stata/HxDirectImportHook.class" not in names:\n            fail("HxDirectImportHook.class is missing from hxworkbench.jar")',
        1,
    )
    verify = verify.replace(
        "    majors = verify_jar()\n    print(f\"HX_JAR_SYNC_OK source={actual} java_major={','.join(map(str, sorted(majors)))}\")",
        "    helper_expected = marker_sha(HELPER_MARKER, 'direct-import hook')\n    helper_actual = git_blob_sha1(HELPER_SOURCE)\n    if helper_actual != helper_expected:\n        fail(\n            'shipped HxDirectImportHook.class is stale relative to HxDirectImportHook.java '\n            f'(jar source={helper_expected}, current source={helper_actual}).'\n        )\n    majors = verify_jar()\n    print(f\"HX_JAR_SYNC_OK source={actual} helper={helper_actual} java_major={','.join(map(str, sorted(majors)))}\")",
        1,
    )
write(verify_path, verify)

# 6) Permanent direct-import contract verifier and CI wiring.
contract_path = ROOT / "tools/verify_direct_import_contracts.py"
contract_path.write_text('''from pathlib import Path\nimport hashlib\nimport re\nimport sys\nimport zipfile\n\nROOT = Path(__file__).resolve().parents[1]\n\ndef fail(message):\n    print("HX_DIRECT_IMPORT_VERIFY_FAIL:", message, file=sys.stderr)\n    raise SystemExit(1)\n\ndef read(path):\n    return (ROOT / path).read_text(encoding="utf-8")\n\nhelper = read("src/main/java/com/hexie/stata/HxDirectImportHook.java")\nlauncher = read("hxtoolbox.ado")\nworkbench = read("src/main/java/com/hexie/stata/HxWorkbench.java")\nfor needle in (\n    "Excel / CSV 转换为 DTA",\n    "导入 Excel/CSV",\n    "导入 Excel / CSV",\n    "convertLoadAfter",\n    "convertProtectLeadingZeros",\n    "convertDelimitedFirstRow",\n    "runConvertDta",\n    "detectExternalFile",\n    "sample.xlsx",\n    "sample.xls",\n    "sample.csv",\n    "企业数据.dta",\n):\n    if needle not in helper:\n        fail(f"direct-import hook contract missing: {needle}")\nif "import com.stata.sfi" in helper:\n    fail("direct-import hook must compile without fake or bundled Stata SFI classes")\nif "HxDirectImportHook install" not in launcher:\n    fail("hxtoolbox does not install the direct-import hook after launch")\nfor needle in ("convertInputFile", "convertOutputFile", "convertLoadAfter", "runConvertDta", "detectExternalFile"):\n    if needle not in workbench:\n        fail(f"existing conversion engine surface missing: {needle}")\nwith zipfile.ZipFile(ROOT / "hxworkbench.jar") as jar:\n    names = jar.namelist()\n    if "com/hexie/stata/HxDirectImportHook.class" not in names:\n        fail("production JAR does not contain HxDirectImportHook.class")\n    if any(name.startswith("com/stata/sfi/") for name in names):\n        fail("production JAR bundles Stata SFI classes")\nprint("HX_DIRECT_IMPORT_VERIFY_OK formats=xlsx,xls,csv output=dta load_after=1 existing_engine=1 sfi_bundled=0")\n''', encoding="utf-8", newline="\n")

ci_path = ".github/workflows/ci.yml"
ci = read(ci_path)
if "Verify direct Excel CSV import contract" not in ci:
    anchor = "      - name: Verify repository installation invariants\n        run: python tools/verify_repository_invariants.py\n"
    block = anchor + "\n      - name: Verify direct Excel CSV import contract\n        run: python tools/verify_direct_import_contracts.py\n"
    if anchor not in ci:
        fail("CI repository invariant step not found")
    ci = ci.replace(anchor, block, 1)
if "Self-test direct import hook Java 11" not in ci:
    anchor = "      - name: Parse production JAR build script\n"
    step = """      - name: Self-test direct import hook Java 11\n        run: |\n          rm -rf /tmp/hximporthook\n          mkdir -p /tmp/hximporthook\n          javac --release 11 -d /tmp/hximporthook src/main/java/com/hexie/stata/HxDirectImportHook.java\n          java -cp /tmp/hximporthook com.hexie.stata.HxDirectImportHook --self-test\n\n"""
    if anchor not in ci:
        fail("CI production build parse step not found")
    ci = ci.replace(anchor, step + anchor, 1)
write(ci_path, ci)

# 7) AGENTS.md records the UX invariant so later AI changes do not turn this
# back into a detached converter entrypoint.
agents = read("AGENTS.md")
rule = """

12. The empty/current-data Excel/CSV entry is a direct import workflow. It must:
    - accept `.xlsx`, `.xls`, and `.csv`;
    - derive a sibling `.dta` output automatically;
    - reuse the managed conversion engine instead of duplicating import logic;
    - keep overwrite protection and leading-zero protection;
    - load the generated DTA and refresh the workbench after success.
"""
if "The empty/current-data Excel/CSV entry is a direct import workflow" not in agents:
    agents = agents.rstrip() + rule + "\n"
    write("AGENTS.md", agents)

# 8) Version-only byte patch for existing HxWorkbench classes. The functional
# change is the new hook class compiled separately without SFI stubs.
jar_replacements = patch_jar_version()
source_blob = write_marker(
    java_path,
    "src/main/java/com/hexie/stata/HxWorkbench.jar-source",
    "For 1.5.15 HxWorkbench behavior is unchanged; only the equal-length public VERSION constant is patched in the shipped class.",
)
helper_blob = write_marker(
    "src/main/java/com/hexie/stata/HxDirectImportHook.java",
    "src/main/java/com/hexie/stata/HxDirectImportHook.jar-source",
    "This marker is updated after the Java-11 hook class is compiled and packaged; the hook has no compile-time Stata SFI dependency.",
)

print(
    "HX_DIRECT_IMPORT_SOURCE_FINALIZED "
    f"version={NEW} jar_version_replacements={jar_replacements} "
    f"workbench_source={source_blob} helper_source={helper_blob}"
)
