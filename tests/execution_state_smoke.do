version 17.0
clear all
set more off
args repository
adopath ++ `"`repository'"'
set obs 20
generate double x = _n
quietly summarize x
local expected = r(mean)
hxexecute, command("generate double centered = x - r(mean)")
assert centered == x - `expected'
hxexecute, command("summarize x, detail")
assert r(mean) == 10.5
assert r(p50) == 10.5
assert r(rc) == 0
quietly hxrefresh
assert r(mean) == 10.5
hxcontext, command("quietly hxresolve regress")
assert r(mean) == 10.5
hxcontext, command("quietly count if x > 10")
assert r(mean) == 10.5

* Preserve matrices and macros as well as scalars.
hxexecute, command("correlate x centered")
matrix actual = r(C)
assert el(actual, 1, 2) == 1
program define hx_test_returns, rclass
    return local sample "complete sample"
    return scalar answer = 42
end
hxexecute, command("hx_test_returns")
assert r(answer) == 42
assert `"`r(sample)'"' == "complete sample"

set seed 4567
generate double expected_draw = runiform()
local expected_state `"`c(rngstate)'"'
generate double actual_draw = 0
char _dta[hxtoolbox_monitor_command] "replace"
char _dta[hxtoolbox_monitor_depvar] "actual_draw"
char _dta[hxtoolbox_monitor_expression] "runiform()"
set seed 4567
hxexecute, command("replace actual_draw = runiform()")
assert actual_draw == expected_draw
assert `"`c(rngstate)'"' == `"`expected_state'"'

* Refreshing a preview repeatedly must leave both streams unchanged.
local rng_before `"`c(rngstate)'"'
local sort_before `"`c(sortrngstate)'"'
forvalues i=1/3 {
    hxmonitor, action(refresh) command(replace) depvar(actual_draw) expression("runiform()")
}
assert `"`c(rngstate)'"' == `"`rng_before'"'
assert `"`c(sortrngstate)'"' == `"`sort_before'"'

* Failure reports the native code and does not change the data.
capture noisily hxexecute, command("replace absent_variable = 1")
assert _rc == 111
assert actual_draw == expected_draw
assert _N == 20
quietly regress centered x
hxcontext, command("quietly hxresolve regress")
hxcontext, command("quietly hxrefresh")
assert e(sample) == 1
quietly margins, at(x=(5 10))
display as result "HX_EXECUTION_STATE_SMOKE_OK"
