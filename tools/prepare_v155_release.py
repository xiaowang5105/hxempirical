from __future__ import annotations

from pathlib import Path
import base64
import hashlib
import shutil
import struct
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OLD_VERSION = "1.5.4"
NEW_VERSION = "1.5.5"
RELEASE_TIME = "2026-08-15 19:21（UTC+8）"
CHUNK_CHARS = 49152


def fail(message: str) -> None:
    raise SystemExit(f"HX_PREPARE_RELEASE_FAIL: {message}")


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write_text(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8", newline="\n")


def replace_exact(text: str, old: str, new: str, label: str, count: int | None = 1) -> str:
    hits = text.count(old)
    if count is not None and hits != count:
        fail(f"{label}: expected {count} occurrence(s), found {hits}")
    if hits == 0:
        fail(f"{label}: target text not found")
    return text.replace(old, new, hits if count is None else count)


def update_versions_and_docs() -> None:
    pkg = read_text("hxempirical.pkg")
    pkg = replace_exact(pkg, "d Version 1.5.4", "d Version 1.5.5", "package version")
    write_text("hxempirical.pkg", pkg)

    entry = read_text("hxempirical.ado")
    entry = entry.replace("1.5.4", "1.5.5")
    if "1.5.4" in entry or "1.5.5" not in entry:
        fail("hxempirical.ado version update failed")
    write_text("hxempirical.ado", entry)

    help_text = read_text("hxempirical.sthlp")
    help_text = help_text.replace("1.5.4", "1.5.5")
    if "1.5.4" in help_text or "1.5.5" not in help_text:
        fail("hxempirical.sthlp version update failed")
    write_text("hxempirical.sthlp", help_text)

    for path, old, new in (
        ("hxinstall.do", "*! hxinstall 1.5.4  15aug2026", "*! hxinstall 1.5.5  15aug2026"),
        ("hxinstaller.ado", "*! hxinstaller 1.5.4  15aug2026", "*! hxinstaller 1.5.5  15aug2026"),
    ):
        text = read_text(path)
        text = replace_exact(text, old, new, path)
        write_text(path, text)

    java_path = "src/main/java/com/hexie/stata/HxWorkbench.java"
    java = read_text(java_path)
    java = replace_exact(
        java,
        'public static final String VERSION = "1.5.4";',
        'public static final String VERSION = "1.5.5";',
        "Java VERSION",
    )
    write_text(java_path, java)

    readme = read_text("README.md")
    readme = replace_exact(readme, "**当前发布版本：1.5.4**", "**当前发布版本：1.5.5**", "README current version")
    readme = replace_exact(
        readme,
        "**上次修改时间：2026-08-15 17:10（UTC+8）**",
        f"**上次修改时间：{RELEASE_TIME}**",
        "README modified time",
    )
    release_intro = """### 1.5.5 OneClick 依赖与发布一致性

- `oneclick` 按真实外部命令使用；hxempirical 从 SSC 安装时先安装其依赖 `tuples`，再安装 `oneclick`，并在安装后再次检查两者是否可用。
- `oneclick_robustness` 按作者扩展处理；当前 hxempirical 未配置经过验证的 SSC 自动安装源，需要按作者发布说明手动安装，安装后工具箱会自动识别。
- 旧 HX `did_builder` / `did_trends` 仅保留兼容调用，不再进入公共搜索目录；标准 DID 继续直接使用 Stata 官方 `didregress` / `xtdidregress`。
- 发布一致性 CI 增加 ZIP 内文件与仓库受管文件的逐字节核对，避免“源码已更新、安装包仍是旧文件”的发布漂移。

"""
    readme = replace_exact(
        readme,
        "### 1.5.4 数据表运算与外部命令\n",
        release_intro + "### 1.5.4 数据表运算与外部命令\n",
        "README release intro",
    )
    oneclick_old = "OneClick 专区执行的是作者发布的真实外部命令。候选控制变量仍应依据理论、文献与识别设计确定。"
    oneclick_new = """OneClick 专区执行的是作者发布的真实外部命令。`oneclick` 通过 SSC 安装，且依赖 `tuples`；hxempirical 会按 `tuples → oneclick` 的顺序安装并验证。`oneclick_robustness` 按作者扩展处理，当前未配置经过验证的 SSC 自动安装源，需要按作者发布说明手动安装；安装完成后 hxempirical 会自动识别。

候选控制变量仍应依据理论、文献与识别设计确定。"""
    readme = replace_exact(readme, oneclick_old, oneclick_new, "README OneClick source note")
    history_old = "## 版本记录\n\n### 1.5.4（当前版本）\n"
    history_new = f"""## 版本记录

### 1.5.5（当前版本）

**发布时间**：{RELEASE_TIME}

**修改内容**：

- 修复 `oneclick` 自动安装遗漏 `tuples` 依赖的问题，并在安装后验证依赖完整性。
- 明确 `oneclick_robustness` 为需按作者说明手动安装的扩展；旧 HX DID helper 从公共搜索目录移除，官方 DID 保持公开。
- 强化发布一致性检查：CI 逐字节核对 release ZIP 与仓库受管文件，并重新构建 Java JAR、ZIP、Base64 分段及 SHA-256 索引。

### 1.5.4
"""
    readme = replace_exact(readme, history_old, history_new, "README version history")
    write_text("README.md", readme)

    install = read_text("INSTALL.md")
    install = replace_exact(install, "当前版本：1.5.4", "当前版本：1.5.5", "INSTALL current version")
    install = replace_exact(install, "最新版本：1.5.4", "最新版本：1.5.5", "INSTALL latest version")
    optional_old = "`reghdfe`、`winsor2`、`ivreghdfe`、`ppmlhdfe`、`oneclick`、`oneclick_robustness`、`coefplot`、`event_plot` 是可选扩展。它们缺失时，核心工作台和 Stata 官方命令仍然可用。"
    optional_new = optional_old + " `oneclick` 可由 hxempirical 从 SSC 按 `tuples → oneclick` 顺序安装；`oneclick_robustness` 当前没有配置经过验证的 SSC 自动安装源，需要按作者发布说明手动安装。"
    install = replace_exact(install, optional_old, optional_new, "INSTALL OneClick source note")
    write_text("INSTALL.md", install)


def write_verify_release() -> None:
    content = '''from pathlib import Path
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
'''
    write_text("tools/verify_release.py", content)


def create_sfi_stubs(stub_root: Path) -> list[Path]:
    package = stub_root / "com" / "stata" / "sfi"
    package.mkdir(parents=True, exist_ok=True)
    sources = {
        "SFIToolkit.java": '''package com.stata.sfi;
public class SFIToolkit {
  public static int executeCommand(String s, boolean b){return 0;}
  public static void displayln(String s){}
  public static void errorln(String s){}
  public static String stackTraceToString(Throwable t){return t==null?"":t.toString();}
}
''',
        "Characteristic.java": 'package com.stata.sfi;\npublic class Characteristic { public static String getDtaChar(String s){return "";} }\n',
        "Macro.java": 'package com.stata.sfi;\npublic class Macro { public static String getGlobal(String s){return "";} }\n',
        "Missing.java": 'package com.stata.sfi;\npublic class Missing { public static boolean isMissing(double v){return Double.isNaN(v);} }\n',
        "Scalar.java": 'package com.stata.sfi;\npublic class Scalar { public static double getValue(String s){return Double.NaN;} }\n',
        "Data.java": '''package com.stata.sfi;
public class Data {
  public static long getObsTotal(){return 0L;}
  public static int getVarCount(){return 0;}
  public static int getVarIndex(String s){return 0;}
  public static String getVarName(int i){return "";}
  public static String getVarLabel(int i){return "";}
  public static String getVarFormat(int i){return "";}
  public static boolean isVarTypeString(int i){return false;}
  public static double getNum(int i,long j){return Double.NaN;}
  public static String getStr(int i,long j){return "";}
  public static String getFormattedValue(int i,long j,boolean b){return "";}
}
''',
        "Frame.java": '''package com.stata.sfi;
public class Frame {
  public static Frame connect(String s){return new Frame();}
  public static Frame create(String s){return new Frame();}
  public void drop(){}
  public long getObsTotal(){return 0L;}
  public int getVarCount(){return 0;}
  public int getVarIndex(String s){return 0;}
  public String getVarName(int i){return "";}
  public boolean isVarTypeString(int i){return false;}
  public double getNum(int i,long j){return Double.NaN;}
  public String getStr(int i,long j){return "";}
  public String getFormattedValue(int i,long j,boolean b){return "";}
}
''',
    }
    paths = []
    for name, source in sources.items():
        path = package / name
        path.write_text(source, encoding="utf-8")
        paths.append(path)
    return paths


def rebuild_jar() -> None:
    jar_path = ROOT / "hxworkbench.jar"
    source = ROOT / "src/main/java/com/hexie/stata/HxWorkbench.java"
    if not jar_path.is_file():
        fail("hxworkbench.jar missing")
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        stub_root = td_path / "sfi"
        classes = td_path / "classes"
        classes.mkdir()
        stubs = create_sfi_stubs(stub_root)
        cmd = [
            "javac",
            "--release",
            "11",
            "-encoding",
            "UTF-8",
            "-Xmaxerrs",
            "200",
            "-d",
            str(classes),
            *(str(p) for p in stubs),
            str(source),
        ]
        subprocess.run(cmd, check=True, cwd=ROOT)

        built = sorted((classes / "com/hexie/stata").glob("HxWorkbench*.class"))
        if not built:
            fail("Java compile produced no HxWorkbench classes")

        replacement = jar_path.with_suffix(".jar.new")
        with zipfile.ZipFile(jar_path, "r") as old, zipfile.ZipFile(replacement, "w") as new:
            for info in old.infolist():
                if info.filename.startswith("com/hexie/stata/HxWorkbench") and info.filename.endswith(".class"):
                    continue
                new.writestr(info, old.read(info.filename))
            for class_file in built:
                arcname = class_file.relative_to(classes).as_posix()
                new.write(class_file, arcname, compress_type=zipfile.ZIP_DEFLATED)
        replacement.replace(jar_path)

    majors = set()
    version_found = False
    with zipfile.ZipFile(jar_path) as jar:
        for name in jar.namelist():
            if not name.endswith(".class"):
                continue
            data = jar.read(name)
            if len(data) < 8:
                fail("invalid class file in JAR: " + name)
            magic, _, major = struct.unpack(">IHH", data[:8])
            if magic != 0xCAFEBABE:
                fail("invalid class magic: " + name)
            majors.add(major)
            if NEW_VERSION.encode() in data:
                version_found = True
    if not majors or max(majors) > 55:
        fail(f"Java class level too new: {sorted(majors)}")
    if not version_found:
        fail("rebuilt JAR does not contain v1.5.5")


def rebuild_release_bundle() -> tuple[int, int, str]:
    pkg_lines = read_text("hxempirical.pkg").splitlines()
    managed = [line.split(None, 1)[1].strip() for line in pkg_lines if line.startswith("f ")]
    bundle = []
    for rel in managed + ["hxempirical.pkg", "hxinstall.do", "hxinstall_offline.do", "INSTALL.md"]:
        if rel not in bundle:
            bundle.append(rel)
        if not (ROOT / rel).is_file():
            fail("bundle input missing: " + rel)

    release_dir = ROOT / "release"
    release_dir.mkdir(exist_ok=True)
    for old_part in release_dir.glob("hxempirical-release.b64.*"):
        old_part.unlink()

    archive = ROOT / "hxempirical-release.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in bundle:
            z.write(ROOT / rel, rel)

    raw = archive.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    part_names = []
    for index, offset in enumerate(range(0, len(encoded), CHUNK_CHARS), start=1):
        part_name = f"release/hxempirical-release.b64.{index:03d}"
        chunk = encoded[offset : offset + CHUNK_CHARS]
        lines = [chunk[i : i + 76] for i in range(0, len(chunk), 76)]
        (ROOT / part_name).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        part_names.append(part_name)

    sha256 = hashlib.sha256(raw).hexdigest()
    index_lines = [
        "v 1",
        "d archive hxempirical-release.zip",
        f"d bytes {len(raw)}",
        f"d sha256 {sha256}",
        f"d parts {len(part_names)}",
        *(f"f {name}" for name in part_names),
    ]
    write_text("hxempirical-release.index", "\n".join(index_lines) + "\n")
    return len(raw), len(part_names), sha256


def main() -> None:
    update_versions_and_docs()
    write_verify_release()
    rebuild_jar()
    size, parts, sha = rebuild_release_bundle()
    subprocess.run(["python", "tools/verify_release.py"], cwd=ROOT, check=True)
    subprocess.run(["python", "tools/verify_static_contracts.py"], cwd=ROOT, check=True)

    # One-shot automation cleans itself from the final release tree.
    for rel in ("tools/prepare_v155_release.py", ".github/workflows/release-sync.yml"):
        path = ROOT / rel
        if path.exists():
            path.unlink()

    print(f"HX_PREPARE_RELEASE_OK version={NEW_VERSION} bytes={size} parts={parts} sha256={sha}")


if __name__ == "__main__":
    main()
