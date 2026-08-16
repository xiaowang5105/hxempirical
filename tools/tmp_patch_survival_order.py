from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.25  16aug2026", "*! hxregistry 3.1.26  16aug2026", "registry version")
old = '''    else if inlist(`"`method'"', "生存分析", "survival") {
        local view "ctset cttost ltable snapspan stset stdescribe stsum stci stcurve stbase stfill stgen stsplit stvary sttocc sttoct"
        local view "`view' sts stcox streg stintreg"
        if c(stata_version) >= 17 local view "`view' stintcox"
        local view "`view' stcrreg stir strate stptime stmh stmc"
    }
'''
new = '''    else if inlist(`"`method'"', "生存分析", "survival") {
        /* Common estimation workflow first; data-management and legacy rate tools later. */
        local view "stset stcox streg stintreg"
        if c(stata_version) >= 17 local view "`view' stintcox"
        local view "`view' stcrreg sts stcurve stdescribe stsum stci"
        local view "`view' stbase stfill stgen stsplit stvary sttocc sttoct"
        local view "`view' stir strate stptime stmh stmc ctset cttost ltable snapspan"
    }
'''
r = once(r, old, new, "survival method order")
rp.write_text(r, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'if "选择模型" not in stats_methods:\n    fail("public Selection models method missing")\n'
checks = '''if 'local view "stset stcox streg stintreg"' not in registry:
    fail("survival navigation must start with the common declaration/estimation workflow")
if "if c(stata_version) >= 17 local view \"`view' stintcox\"" not in registry:
    fail("stintcox must remain gated to Stata 17+")
'''
v = once(v, anchor, anchor + checks, "survival-order static contract anchor")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_SURVIVAL_ORDER_PATCH_OK")
