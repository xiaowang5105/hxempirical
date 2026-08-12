from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing pattern: {label}")
    return text.replace(old, new, 1)


java_path = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
java = java_path.read_text(encoding="utf-8")

if 'public static final String VERSION = "1.0.2";' not in java:
    java = replace_once(
        java,
        'public static final String VERSION = "1.0.1";',
        'public static final String VERSION = "1.0.2";',
        "java version",
    )
    java = replace_once(
        java,
        'SFIToolkit.displayln("HxWorkbench 1.0.1");',
        'SFIToolkit.displayln("HxWorkbench 1.0.2");',
        "java version output",
    )
    java = replace_once(
        java,
        '            HxWorkbench.StataBridge.execute("help " + var1, true);',
        '            int var2 = HxWorkbench.StataBridge.execute("help " + var1, true);\n'
        '            if (var2 == 0) {\n'
        '               HxWorkbench.StataBridge.execute("capture window manage forward viewer", false);\n'
        '            }',
        "help viewer foreground",
    )
    java_path.write_text(java, encoding="utf-8")


pkg_path = Path("hxempirical.pkg")
pkg = pkg_path.read_text(encoding="utf-8")
if "d Version 1.0.1" in pkg:
    pkg = pkg.replace("d Version 1.0.1", "d Version 1.0.2", 1)
pkg_path.write_text(pkg, encoding="utf-8")


ado_path = Path("hxempirical.ado")
ado = ado_path.read_text(encoding="utf-8")
ado = ado.replace("*! hxempirical 1.0.1  12aug2026", "*! hxempirical 1.0.2  12aug2026", 1)
ado = ado.replace('display as text "版本：" as result "1.0.1"', 'display as text "版本：" as result "1.0.2"', 1)
ado = ado.replace('return local version "1.0.1"', 'return local version "1.0.2"', 1)
ado_path.write_text(ado, encoding="utf-8")


help_path = Path("hxempirical.sthlp")
help_text = help_path.read_text(encoding="utf-8")
help_text = help_text.replace("{* *! version 1.0.1  12aug2026}{...}", "{* *! version 1.0.2  12aug2026}{...}", 1)
help_text = help_text.replace("package version 1.0.1.", "package version 1.0.2.", 1)
help_path.write_text(help_text, encoding="utf-8")


readme_path = Path("README.md")
readme = readme_path.read_text(encoding="utf-8")
if "### 1.0.2（当前版本）" not in readme:
    readme = replace_once(readme, "当前发布版本：**1.0.1**", "当前发布版本：**1.0.2**", "readme version")
    readme = replace_once(
        readme,
        "上次修改时间：**2026-08-12 16:07（UTC+8）**",
        "上次修改时间：**2026-08-12 16:31（UTC+8）**",
        "readme modified time",
    )
    release = "\n".join(
        [
            "### 1.0.2（当前版本）",
            "",
            "**发布时间**：2026-08-12 16:31（UTC+8）",
            "",
            "**修改内容**：",
            "",
            "- 修复工作台点击“查看帮助”后 Stata Viewer 可能被工作台窗口遮挡的问题。帮助命令成功打开后，继续调用 Stata 官方 `window manage forward viewer` 将 Viewer 窗口置于最前；不再需要手动最小化或切换工作台才能看到帮助页。",
            "- 该修复只调整窗口前后顺序，不改变帮助内容、命令解析、回归执行或数据处理逻辑。",
            "- 同步更新 Java 工作台、Stata 入口、package manifest、help 与 README 版本为 **1.0.2**，并重新构建 `hxworkbench.jar`。",
            "",
            "### 1.0.1",
        ]
    )
    readme = replace_once(readme, "### 1.0.1（当前版本）", release, "readme release section")
    readme_path.write_text(readme, encoding="utf-8")


assert 'public static final String VERSION = "1.0.2";' in java_path.read_text(encoding="utf-8")
assert 'capture window manage forward viewer' in java_path.read_text(encoding="utf-8")
assert "d Version 1.0.2" in pkg_path.read_text(encoding="utf-8")
assert "### 1.0.2（当前版本）" in readme_path.read_text(encoding="utf-8")

print("HX_HELP_VIEWER_102_PATCH_OK")
