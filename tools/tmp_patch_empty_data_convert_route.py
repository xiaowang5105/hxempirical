from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
j = once(
    j,
    '         var8.addActionListener(var1x -> this.openCommandPage("import"));',
    '         var8.addActionListener(var1x -> this.openCommandPage("hxconvert"));',
    "empty-data convert route",
)
jp.write_text(j, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = '''if "工作台只检测是否已安装，不再自动安装" not in readme:
    fail("README current external-command policy is not manual-only")
'''
checks = '''if 'JButton var8 = new JButton("Excel / CSV 转换为 DTA")' not in java:
    fail("empty-data conversion action is missing")
if 'var8.addActionListener(var1x -> this.openCommandPage("hxconvert"));' not in java:
    fail("empty-data conversion action must route to the safe hxconvert workflow")
if 'var8.addActionListener(var1x -> this.openCommandPage("import"));' in java:
    fail("empty-data conversion action still routes to generic import instead of hxconvert")
'''
v = once(v, anchor, anchor + checks, "empty-data conversion contract anchor")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_EMPTY_DATA_CONVERT_ROUTE_PATCH_OK")
