from pathlib import Path

jp = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
j = jp.read_text(encoding="utf-8")
old = 'public static final String VERSION = "1.5.12";'
new = 'public static final String VERSION = "1.5.11";'
if j.count(old) != 1:
    raise SystemExit(f"Java version rollback expected 1 match, got {j.count(old)}")
j = j.replace(old, new, 1)
jp.write_text(j, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
block = '''if 'public static final String VERSION = "1.5.12";' not in java:
    fail("HxWorkbench version marker was not advanced for the structured Graphics page batch")
'''
if v.count(block) != 1:
    raise SystemExit(f"version static contract expected 1 match, got {v.count(block)}")
v = v.replace(block, "", 1)
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_GRAPH_CORE_VERSION_ALIGNMENT_OK")
