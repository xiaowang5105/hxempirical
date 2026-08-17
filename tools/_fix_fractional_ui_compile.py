from pathlib import Path

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')
old = 'this.softList('
if s.count(old) != 3:
    raise SystemExit(f'HX_FRACTIONAL_LIST_FIX_FAIL {s.count(old)}')
p.write_text(s.replace(old, 'this.listPane('), encoding='utf-8')
print('HX_FRACTIONAL_LIST_FIX_OK')
