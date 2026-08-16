from pathlib import Path

p = Path("tools/verify_static_contracts.py")
s = p.read_text(encoding="utf-8")
old = '''for gated in ("dtable", "gsbounds", "gsdesign"):
    if f'foreach cmd in mediate hdidregress xthdidregress bmaregress dtable gsbounds gsdesign' not in registry:
        fail("Stata 18 summary/power version gate missing")
'''
new = '''for gated in ("dtable", "gsbounds", "gsdesign"):
    if gated not in stats_cmds:
        fail(f"Stata 18 summary/power command missing: {gated}")
if "dtable gsbounds gsdesign" not in registry:
    fail("Stata 18 summary/power version gate missing")
'''
if old not in s:
    raise SystemExit("legacy Stata18 summary/power gate contract anchor missing")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_BAYESIAN_GATE_CONTRACT_REFRESH_OK")
