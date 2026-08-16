from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)

rp = Path("hxregistry.ado")
r = rp.read_text(encoding="utf-8")
r = once(r, "*! hxregistry 3.1.26  16aug2026", "*! hxregistry 3.1.27  16aug2026", "registry version")
old_mts = '''    else if inlist(`"`method'"', "多元时间序列", "multivariate_ts") {
        local view "var svar vec varbasic varsoc vargranger varlmar varnorm varstable varwle vecrank veclmar vecnorm vecstable irf"
        if c(stata_version) >= 18 local view "`view' lpirf"
        local view "`view' mgarch dfactor sspace xcorr"
    }
'''
new_mts = '''    else if inlist(`"`method'"', "多元时间序列", "multivariate_ts") {
        /* Put the routine VAR workflow before structural/specialized systems. */
        local view "var varsoc vargranger varlmar varnorm varstable irf"
        if c(stata_version) >= 18 local view "`view' lpirf"
        local view "`view' svar vec vecrank veclmar vecnorm vecstable varbasic varwle"
        local view "`view' mgarch dfactor sspace xcorr"
    }
'''
r = once(r, old_mts, new_mts, "multivariate time-series order")
old_causal = '''    else if inlist(`"`method'"', "因果推断/处理效应", "causal_treatment") {
        local view "teffects eteffects etregress etpoisson stteffects"
        if c(stata_version) >= 17 local view "`view' didregress xtdidregress telasso"
        if c(stata_version) >= 18 local view "`view' mediate hdidregress xthdidregress"
    }
'''
new_causal = '''    else if inlist(`"`method'"', "因果推断/处理效应", "causal_treatment") {
        /* Surface common DID estimators first when the installed Stata supports them. */
        local view ""
        if c(stata_version) >= 17 local view "didregress xtdidregress"
        if c(stata_version) >= 18 local view "`view' hdidregress xthdidregress mediate"
        local view "`view' teffects eteffects etregress etpoisson stteffects"
        if c(stata_version) >= 17 local view "`view' telasso"
        local view = trim(itrim("`view'"))
    }
'''
r = once(r, old_causal, new_causal, "causal order")
rp.write_text(r, encoding="utf-8", newline="\n")

vp = Path("tools/verify_static_contracts.py")
v = vp.read_text(encoding="utf-8")
anchor = 'if \'local view "stset stcox streg stintreg"\' not in registry:\n    fail("survival navigation must start with the common declaration/estimation workflow")\n'
checks = '''if 'local view "var varsoc vargranger varlmar varnorm varstable irf"' not in registry:
    fail("multivariate time-series navigation must start with the routine VAR workflow")
if 'if c(stata_version) >= 17 local view "didregress xtdidregress"' not in registry:
    fail("Stata 17+ causal navigation must surface DID estimators first")
'''
v = once(v, anchor, anchor + checks, "common-first ordering static contract anchor")
vp.write_text(v, encoding="utf-8", newline="\n")
print("HX_COMMON_FIRST_STATS_ORDER_PATCH_OK")
