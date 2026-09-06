version 17.0
clear all
set more off
args repository
adopath ++ `"`repository'"'
set obs 100
generate double x = _n
generate double y = 2*x + sin(x)
quietly regress y x, vce(robust)
matrix expected_b = e(b)
local n = _N
local k = c(k)
local filename `"`c(filename)'"'
local rng `"`c(rngstate)'"'
tempfile snapshot model
quietly summarize x
hxproject snapshot using `"`snapshot'"'
assert r(mean) == 50.5
assert _N == `n' & c(k) == `k'
assert `"`c(filename)'"' == `"`filename'"'
assert `"`c(rngstate)'"' == `"`rng'"'
confirm file `"`snapshot'"'
hxproject model using `"`model'"'
assert r(mean) == 50.5
assert _N == `n' & c(k) == `k'
assert e(N) == 100
assert mreldif(e(b),expected_b) == 0
confirm file `"`model'.ster"'
confirm file `"`model'.tsv"'
confirm file `"`model'.sample"'
local signature : char _dta[hxproject_signature]
assert `"`signature'"' != ""
capture noisily hxproject snapshot using `"`snapshot'"'
assert _rc == 602
assert _N == `n' & c(k) == `k'
erase `"`model'.ster"'
erase `"`model'.tsv"'
erase `"`model'.sample"'
display as result "HX_PROJECT_STATE_SMOKE_OK"
