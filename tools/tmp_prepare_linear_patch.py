from pathlib import Path

p = Path("tools/tmp_patch_linear_catalog.py")
text = p.read_text(encoding="utf-8")
old = '''r = once(
    r,
    "regress areg reghdfe cnsreg rreg qreg iqreg bsqreg vwls eivreg sureg mvreg correlate pwcorr",
    "regress areg reghdfe cnsreg rreg hetregress qreg iqreg bsqreg sqreg vwls eivreg intreg tobit truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate pwcorr",
    "linear catalog",
)
'''
new = '''linear_old = "regress areg reghdfe cnsreg rreg qreg iqreg bsqreg vwls eivreg sureg mvreg correlate pwcorr"
linear_new = "regress areg reghdfe cnsreg rreg hetregress qreg iqreg bsqreg sqreg vwls eivreg intreg tobit truncreg boxcox fp nl nlsur gmm sureg reg3 mvreg frontier correlate pwcorr"
if linear_old not in r:
    raise SystemExit("linear catalog anchor missing")
r = r.replace(linear_old, linear_new, 1)
'''
if old not in text:
    raise SystemExit("linear catalog patch block not found")
p.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
print("HX_LINEAR_PATCH_PREPARE_OK")
