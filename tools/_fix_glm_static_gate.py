from pathlib import Path

p = Path('tools/verify_static_contracts.py')
s = p.read_text(encoding='utf-8')

old = "    '默认（power -2）',\n"
new = "    'if (\"igaussian\".equals(family)) return \"power -2\";',\n"
if s.count(old) != 1:
    raise SystemExit(f'HX_GLM_GATE_FIX_FAIL igaussian: {s.count(old)}')
s = s.replace(old, new)

old = "    '默认（power -1）',\n"
new = "    'if (\"gamma\".equals(family)) return \"power -1\";',\n"
if s.count(old) != 1:
    raise SystemExit(f'HX_GLM_GATE_FIX_FAIL gamma: {s.count(old)}')
s = s.replace(old, new)

old = "    'this.time.addItem(\"opower #\")',\n"
new = "    'this.time.addItem(\"默认（\" + canonical + \"）\")',\n    'this.time.addItem(\"opower #\")',\n"
if s.count(old) != 1:
    raise SystemExit(f'HX_GLM_GATE_FIX_FAIL generated-label: {s.count(old)}')
s = s.replace(old, new)

p.write_text(s, encoding='utf-8')
print('HX_GLM_GATE_FIX_OK')
