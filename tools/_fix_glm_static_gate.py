from pathlib import Path
p = Path('tools/verify_static_contracts.py')
s = p.read_text(encoding='utf-8')
repls = {
    "    '默认（power -2）',\n": "    'if (\"igaussian\".equals(family)) return \"power -2\";',\n",
    "    '默认（power -1）',\n": "    'if (\"gamma\".equals(family)) return \"power -1\";',\n    "    'this.time.addItem(\"opower #\")',\n": "    'this.time.addItem(\"默认（\" + canonical + \"）\")',\n    'this.time.addItem(\"opower #\")',\n",
}
for old, new in repls.items():
    if s.count(old) != 1:
        raise SystemExit(f'HX_GLM_GATE_FIX_FAIL {old!r}: {s.count(old)}')
    s = s.replace(old, new)
p.write_text(s, encoding='utf-8')
print('HX_GLM_GATE_FIX_OK')
