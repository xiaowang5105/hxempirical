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
* Invalid RNG state must not replace live data/results.
capture noisily hxproject restore using `"`snapshot'"', rng(mt64) rngstate(BADSTATE)
assert _rc != 0
assert _N == `n' & c(k) == `k'
assert mreldif(e(b),expected_b) == 0
assert e(sample) == 1
assert `"`c(rngstate)'"' == `"`rng'"'
assert `"`c(filename)'"' == `"`filename'"'
* Read failure after changing RNG must roll back RNG as well.
set seed 987
local other_rng `"`c(rngstate)'"'
set rngstate `rng'
capture noisily hxproject restore using `"`snapshot'.absent"', rng(mt64) rngstate(`other_rng')
assert _rc != 0
assert `"`c(rngstate)'"' == `"`rng'"'
assert mreldif(e(b),expected_b) == 0
assert e(sample) == 1
assert _N == `n' & c(k) == `k'
* Multi-frame snapshots fail explicitly, leaving every frame intact.
frame create lookup
frame lookup: set obs 2
tempfile multifile
capture noisily hxproject snapshot using `"`multifile'"'
assert _rc == 459
frame lookup: assert _N == 2
assert _N == `n'
frame drop lookup
* Successful restore invalidates old estimation results.
replace y = 0
hxproject restore using `"`snapshot'"', rng(mt64) rngstate(`rng')
assert y == 2*x + sin(x)
assert `"`e(cmd)'"' == ""

erase `"`model'.ster"'
erase `"`model'.tsv"'
erase `"`model'.sample"'
display as result "HX_PROJECT_STATE_SMOKE_OK"
