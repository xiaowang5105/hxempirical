from pathlib import Path

p = Path("tools/tmp_patch_count_hurdle_catalog.py")
text = p.read_text(encoding="utf-8")

replacements = [
    (
        '''r = once(
    r,
    "truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate",
    "truncreg churdle boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate",
    "linear hurdle catalog",
)
''',
        '''old = "truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate"
new = "truncreg churdle boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate"
if old not in r:
    raise SystemExit("linear hurdle catalog anchor missing")
r = r.replace(old, new, 1)
''',
    ),
    (
        '''r = once(
    r,
    "poisson nbreg zip zinb tpoisson tnbreg ppmlhdfe",
    "poisson nbreg gnbreg cpoisson zip zinb tpoisson tnbreg ppmlhdfe",
    "count catalog",
)
''',
        '''old = "poisson nbreg zip zinb tpoisson tnbreg ppmlhdfe"
new = "poisson nbreg gnbreg cpoisson zip zinb tpoisson tnbreg ppmlhdfe"
if old not in r:
    raise SystemExit("count catalog anchor missing")
r = r.replace(old, new, 1)
''',
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit("expected catalog patch block not found")
    text = text.replace(old, new, 1)

p.write_text(text, encoding="utf-8", newline="\n")
print("HX_COUNT_HURDLE_PREPARE_OK")
