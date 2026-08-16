from pathlib import Path

p = Path("tools/verify_static_contracts.py")
s = p.read_text(encoding="utf-8")
old = '        fail(f"Stata 18 time-series command missing: {stata18_ts}\n")'
new = '        fail(f"Stata 18 time-series command missing: {stata18_ts}")'
if old not in s:
    raise SystemExit("time-series Stata18 contract newline anchor missing")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_TIMESERIES_CONTRACT_NORMALIZE_OK")
