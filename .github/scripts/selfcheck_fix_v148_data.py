from pathlib import Path

p = Path("src/main/java/com/hexie/stata/HxWorkbench.java")
s = p.read_text(encoding="utf-8")
old = 'return Arrays.asList("缺失值分析", "duplicates");'
new = 'return Arrays.asList("misstable", "duplicates");'
if s.count(old) != 1:
    raise SystemExit(f"data-check preview anchor count={s.count(old)}")
s = s.replace(old, new, 1)
old = 'return Arrays.asList("reshape", "collapse", "xtset");'
new = 'return Arrays.asList("reshape", "collapse", "xtset", "tsset");'
if s.count(old) != 1:
    raise SystemExit(f"data-structure preview anchor count={s.count(old)}")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
