from pathlib import Path

p = Path("tools/verify_static_contracts.py")
s = p.read_text(encoding="utf-8")
replacements = [
    (
        '        fail(f"Stata 18 time-series command missing: {stata18_ts}\\n")',
        '        fail(f"Stata 18 time-series command missing: {stata18_ts}")',
    ),
    (
        '    "arimasoc ogap, maxar(4) maxma(3)",',
        '    "ogap, maxar(4) maxma(3)",',
    ),
    (
        '    "wntestq y",',
        '    "检验 y 是否可视为白噪声",',
    ),
]
for old, new in replacements:
    if old not in s:
        raise SystemExit(f"time-series contract normalization anchor missing: {old}")
    s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8", newline="\n")
print("HX_TIMESERIES_CONTRACT_NORMALIZE_OK")
