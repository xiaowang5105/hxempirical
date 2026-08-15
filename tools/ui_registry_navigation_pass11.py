from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'hxregistry.ado'
s = p.read_text(encoding='utf-8')
old = 'else if inlist(`"`method\'"\', "贝叶斯模型平均", "bma") local view "bma"'
new = 'else if inlist(`"`method\'"\', "贝叶斯模型平均", "bma") local view "bmaregress"'
if old not in s:
    raise SystemExit('BMA navigation marker not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('HX_UI_REGISTRY_NAVIGATION_PASS11_OK')
