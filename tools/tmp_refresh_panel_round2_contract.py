from pathlib import Path

p = Path("tools/verify_static_contracts.py")
s = p.read_text(encoding="utf-8")
old = 'Arrays.asList("xtabond", "xtdpdsys", "xthdidregress")'
new = 'Arrays.asList("xtabond", "xtdpdsys", "xtdpd", "xtunitroot", "xtcointtest", "xthdidregress")'
if old not in s:
    raise SystemExit("legacy xthdid panel-time contract anchor missing")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_PANEL_ROUND2_CONTRACT_REFRESH_OK")
