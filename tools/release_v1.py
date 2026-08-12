from pathlib import Path


def replace_once(path: str, old: str, new: str, label: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"missing pattern for {label}: {path}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


# Package-level version metadata.
replace_once("hxempirical.pkg", "d Version 0.9.7", "d Version 1.0.0", "pkg version")
replace_once("hxempirical.pkg", "d Distribution-Date: 20260811", "d Distribution-Date: 20260812", "pkg distribution date")

ado = Path("hxempirical.ado")
text = ado.read_text(encoding="utf-8")
for old, new, label in [
    ("*! hxempirical 0.9.7  11aug2026", "*! hxempirical 1.0.0  12aug2026", "ado header"),
    ('display as text "版本：" as result "0.9.7"', 'display as text "版本：" as result "1.0.0"', "about version"),
    ('return local version "0.9.7"', 'return local version "1.0.0"', "returned version"),
]:
    if old not in text:
        raise SystemExit(f"missing pattern for {label}: hxempirical.ado")
    text = text.replace(old, new, 1)
ado.write_text(text, encoding="utf-8")

helpf = Path("hxempirical.sthlp")
text = helpf.read_text(encoding="utf-8")
old = "{* *! version 0.9.7  11aug2026}{...}"
new = "{* *! version 1.0.0  12aug2026}{...}"
if old not in text:
    raise SystemExit("missing help version header")
text = text.replace(old, new, 1)
# Any other current-version references in the help page must agree with the package release.
text = text.replace("0.9.7", "1.0.0")
helpf.write_text(text, encoding="utf-8")

# README: the entire 13:37–15:08 development series is one major release.
readme = Path("README.md")
text = readme.read_text(encoding="utf-8")
for old, new, label in [
    ("当前发布版本：**0.9.7**", "当前发布版本：**1.0.0**", "README version"),
    ("上次修改时间：**2026-08-12 15:08（UTC+8）**", "上次修改时间：**2026-08-12 15:46（UTC+8）**", "README modified time"),
]:
    if old not in text:
        raise SystemExit(f"missing pattern for {label}")
    text = text.replace(old, new, 1)

start = text.index("## 修改记录")
end = text.index("## 核心结构")
old_block = text[start:end]
first_timeline = old_block.index("### 2026-08-12")
timeline = old_block[first_timeline:]
timeline = timeline.replace("### 2026-08-12 ", "#### 2026-08-12 ")
new_block = (
    "## 版本记录\n\n"
    "### 1.0.0（当前版本）\n\n"
    "**发布时间**：2026-08-12 15:46（UTC+8）\n\n"
    "**版本说明**：2026-08-12 13:37—15:08 期间完成的普通命令层重构、界面调整、命令生成修正、运行前检查、Java 工作台重建与最终自查，全部统一归入 **hxempirical 1.0.0**。这些记录是同一个大版本的开发过程，不再视为多个独立发布版本。\n\n"
    "#### 1.0.0 开发过程记录\n\n"
    + timeline
)
text = text[:start] + new_block + text[end:]
readme.write_text(text, encoding="utf-8")

# Release consistency checks.
for path in ["README.md", "hxempirical.pkg", "hxempirical.ado", "hxempirical.sthlp"]:
    t = Path(path).read_text(encoding="utf-8")
    if "0.9.7" in t:
        raise SystemExit(f"old package version remains in {path}")

r = readme.read_text(encoding="utf-8")
assert "当前发布版本：**1.0.0**" in r
assert "### 1.0.0（当前版本）" in r
assert "#### 2026-08-12 15:08（UTC+8）" in r
assert "#### 2026-08-12 13:37（UTC+8）" in r
print("HX_RELEASE_1_0_0_METADATA_OK")
