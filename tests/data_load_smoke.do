version 17.0
clear all
set more off
args repository
adopath ++ `"`repository'"'
set obs 20
generate double x = _n
generate double y = 3*x + sin(x)
quietly regress y x
matrix expected_b = e(b)
tempfile valid broken
quietly save `"`valid'"'
local filename `"`c(filename)'"'
local rng `"`c(rngstate)'"'
file open out using `"`broken'"', write text
file write out "incomplete DTA"
file close out
foreach path in `"`broken'"' `"`broken'.absent"' {
    capture noisily hxproject load using `"`path'"'
    assert _rc != 0
    assert _N == 20 & c(k) == 2
    assert y == 3*x + sin(x)
    assert mreldif(e(b),expected_b) == 0
    assert e(sample) == 1
    assert `"`c(filename)'"' == `"`filename'"'
    assert `"`c(rngstate)'"' == `"`rng'"'
}
* Other frames survive a replacement of the active frame.
frame create lookup
frame lookup: set obs 2
replace y = 0
quietly summarize x
hxproject load using `"`valid'"'
assert r(mean) == 10.5
assert y == 3*x + sin(x)
assert `"`e(cmd)'"' == ""
frame lookup: assert _N == 2
assert `"`c(rngstate)'"' == `"`rng'"'
frame drop lookup
display as result "HX_DATA_LOAD_SMOKE_OK"
