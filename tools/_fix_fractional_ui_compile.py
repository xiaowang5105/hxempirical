from pathlib import Path

p = Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s = p.read_text(encoding='utf-8')
repls = {
    'this.softList(this.variables, 7)': 'this.listPane(this.variables)',
    'this.softList(this.absorb, 5)': 'this.listPane(this.absorb)',
}
for old, new in repls.items():
    n = s.count(old)
    expected = 1 if 'variables' in old else 2
    if n != expected:
        raise SystemExit(f'HX_FRACTIONAL_LIST_FIX_FAIL {old}: {n}')
    s = s.replace(old, new)
p.write_text(s, encoding='utf-8')
print('HX_FRACTIONAL_LIST_FIX_OK')
